import streamlit as st
import cv2
import numpy as np
import pandas as pd
from PIL import Image
import io

# [알고리즘 A] 강사님 예시 기반: Canny Edge & Dilation 검출 방식
def analyze_canny_method(image):
    # 1. 그레이스케일 변환 및 가우시안 블러
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # 2. Canny Edge 검출
    edges = cv2.Canny(blurred, 50, 150)
    
    # 3. 크랙 강조를 위한 다이얼레이션(팽창) 연산
    kernel = np.ones((3,3), np.uint8)
    dilated = cv2.dilate(edges, kernel, iterations=1)
    
    # 시각화를 위해 원본에 오버레이 (빨간색 선)
    result_img = image.copy()
    result_img[dilated == 255] = [0, 0, 255]
    
    return dilated, result_img

# [알고리즘 B] 실무 고도화 버전: Adaptive Threshold & 픽셀-mm 정량 분석 방식
def analyze_adaptive_method(image, px_to_mm_ratio, safety_threshold):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # 명암비 강화 (조명 노이즈 극복)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(blurred)
    
    # 적응형 이진화 및 모폴로지 잡음 제거
    binary = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    kernel = np.ones((3,3), np.uint8)
    opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel, iterations=2)
    
    contours, _ = cv2.findContours(closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    result_img = image.copy()
    min_crack_area_px = 50 
    crack_data = []
    
    for contour in contours:
        area_px = cv2.contourArea(contour)
        if area_px > min_crack_area_px:
            x, y, w, h = cv2.boundingRect(contour)
            
            # 물리 단위(mm) 변환
            crack_width_mm = min(w, h) * px_to_mm_ratio
            crack_length_mm = max(w, h) * px_to_mm_ratio
            area_mm2 = area_px * (px_to_mm_ratio ** 2)
            
            status = "⚠️ 구조 검토 필요 (초과)" if crack_width_mm >= safety_threshold else "✅ 안전성 확보 (이하)"
            color = (0, 0, 255) if crack_width_mm >= safety_threshold else (0, 255, 0)
            
            # 결과 바운딩 박스 및 수치 매핑
            cv2.rectangle(result_img, (x, y), (x + w, y + h), color, 2)
            cv2.putText(result_img, f"{crack_width_mm:.2f}mm", (x, y - 5), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
            
            crack_data.append({
                "Crack ID": f"C-{len(crack_data)+1}",
                "균열 폭 (mm)": round(crack_width_mm, 3),
                "균열 길이 (mm)": round(crack_length_mm, 3),
                "균열 면적 (mm²)": round(area_mm2, 3),
                "상태 분류": status
            })
            
    df_cracks = pd.DataFrame(crack_data)
    return closing, result_img, df_cracks

# 2. 통합 웹 UI 구성
st.set_page_config(page_title="통합 건축물 균열 진단 시스템", layout="wide")

st.title("🏢 통합형 철근콘크리트 구조물 균열 진단 시스템")
st.markdown("기초 알고리즘(Canny Edge)과 정밀 고도화 알고리즘(Adaptive)의 결과를 비교 분석하고 정량 데이터를 추출합니다.")

# 사이드바 설정 (선택적 스케일 교정)
st.sidebar.header("⚙️ 분석 파라미터 설정")
enable_calibration = st.sidebar.checkbox("📐 실제 치수(Scale) 수동 교정하기", value=False)

DEFAULT_PX_TO_MM = 0.150 
px_to_mm_ratio = DEFAULT_PX_TO_MM

if enable_calibration:
    calibration_method = st.sidebar.radio("교정 기준 선택", ("사진 촬영 가로 폭(mm) 기준", "1픽셀당 실제 길이(mm) 직접 입력"))
    if calibration_method == "1픽셀당 실제 길이(mm) 직접 입력":
        px_to_mm_ratio = st.sidebar.number_input("1 픽셀의 물리적 크기 (mm/px)", min_value=0.001, max_value=10.000, value=0.150, format="%.3f")
    else:
        real_width_mm = st.sidebar.number_input("촬영된 영역의 실제 가로 길이 (mm)", min_value=10.0, max_value=10000.0, value=400.0)
else:
    st.sidebar.info(f"🤖 자동 치수 추정 모드 작동 중 (1 px ≒ {DEFAULT_PX_TO_MM} mm)")

safety_threshold = st.sidebar.slider("허용 균열 폭 기준 (mm)", min_value=0.1, max_value=1.0, value=0.3, step=0.05)

uploaded_file = st.file_uploader("검사할 구조물 이미지를 업로드하세요", type=['jpg', 'png', 'jpeg'])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    image_np = np.array(image)
    image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
    
    if enable_calibration and calibration_method == "사진 촬영 가로 폭(mm) 기준":
        px_to_mm_ratio = real_width_mm / image_bgr.shape[1]
        st.sidebar.success(f"교정 완료: 1 px ≒ {px_to_mm_ratio:.4f} mm")

    st.markdown("---")
    
    with st.spinner("두 가지 알고리즘 동시 연산 중..."):
        # 두 알고리즘 실행
        canny_mask, canny_result = analyze_canny_method(image_bgr)
        adaptive_mask, adaptive_result, df_cracks = analyze_adaptive_method(image_bgr, px_to_mm_ratio, safety_threshold)
        
        # 웹 출력을 위한 RGB 변환
        canny_res_rgb = cv2.cvtColor(canny_result, cv2.COLOR_BGR2RGB)
        adapt_res_rgb = cv2.cvtColor(adaptive_result, cv2.COLOR_BGR2RGB)
        
        # Step 1. 마스크 단계 비교
        st.subheader("📊 Step 1. 균열 마스크 추출 방식 비교")
        col1, col2 = st.columns(2)
        with col1:
            st.image(canny_mask, caption="A. Canny Edge 기반 이진 마스크 (질감 노이즈 포함 가능)", use_column_width=True, channels="GRAY")
        with col2:
            st.image(adaptive_mask, caption="B. Adaptive Threshold 기반 이진 마스크 (잡음 필터링 완료)", use_column_width=True, channels="GRAY")
            
        st.markdown("---")
        
        # Step 2. 최종 시각화 결과 비교
        st.subheader("🔍 Step 2. 알고리즘별 최종 균열 오버레이 비교")
        col3, col4 = st.columns(2)
        with col3:
            st.image(canny_res_rgb, caption="A. Canny 엣지 매핑 결과", use_column_width=True)
        with col4:
            st.image(adapt_res_rgb, caption="B. 정밀 치수 측정 및 허용 기준 평가 결과 (녹색:안전 / 적색:초과)", use_column_width=True)
            
        st.markdown("---")
        
        # Step 3. 정량 데이터 수집 및 다운로드 (고도화 버전 연동)
        st.subheader("📋 Step 3. 정밀 균열 수치 데이터 데이터베이스")
        if not df_cracks.empty:
            over_limit_count = len(df_cracks[df_cracks["상태 분류"].str.contains("초과")])
            st.metric(label="⚠️ 내구성 기준 초과 균열 개수 (구조 검토 대상)", value=f"{over_limit_count} 개 / 전체 {len(df_cracks)} 개")
            st.dataframe(df_cracks, use_container_width=True)
            
            # Excel 다운로드 기능
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_cracks.to_excel(writer, sheet_name='Crack_Inspection_Report', index=False)
            
            st.download_button(
                label="📊 분석 리포트 엑셀(.xlsx) 파일 다운로드",
                data=buffer.getvalue(),
                file_name="integrated_crack_report.xlsx",
                mime="application/vnd.ms-excel"
            )
        else:
            st.success("고도화 필터 기준, 부재 표면에서 유의미한 크기의 균열이 발견되지 않았습니다.")