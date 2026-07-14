import streamlit as st
import cv2
import numpy as np
import pandas as pd
from PIL import Image
import io

# 1. 크랙 분석 알고리즘 (mm 변환 및 안전 기준 분류 추가)
def analyze_cracks_with_scale(image, px_to_mm_ratio, safety_threshold):
    """
    px_to_mm_ratio: 1 픽셀당 몇 mm인지 나타내는 비율 (mm/px)
    safety_threshold: 구조 안전성 기준 균열 폭 (mm)
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(blurred)
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
            # 바운딩 박스로 대략적인 균열 폭과 길이 산정
            x, y, w, h = cv2.boundingRect(contour)
            
            # 픽셀 단위를 mm 단위로 변환
            # (일반적으로 좁은 방향을 균열 폭, 긴 방향을 균열 길이의 근사치로 가정)
            crack_width_mm = min(w, h) * px_to_mm_ratio
            crack_length_mm = max(w, h) * px_to_mm_ratio
            area_mm2 = area_px * (px_to_mm_ratio ** 2)
            
            # 안전 기준(허용 균열 폭)을 초과하는지 평가
            status = "⚠️ 구조 검토 필요 (초과)" if crack_width_mm >= safety_threshold else "✅ 안전성 확보 (이하)"
            color = (0, 0, 255) if crack_width_mm >= safety_threshold else (0, 255, 0) # 초과는 빨간색, 안전은 초록색
            
            # 경계 상자 시각화
            cv2.rectangle(result_img, (x, y), (x + w, y + h), color, 2)
            cv2.putText(result_img, f"W:{crack_width_mm:.2f}mm", (x, y - 5), 
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

# 2. 웹 UI 구성
st.set_page_config(page_title="콘크리트 구조 진단 실무 웹", layout="wide")

st.title("🏢 철근콘크리트 구조물 균열 진단 & 분석 시스템")
st.markdown("촬영된 크랙 이미지의 픽셀 단위를 **물리적 단위(mm)**로 변환하고, 설계 기준상 허용 균열 폭과 비교 분석합니다.")

# 사이드바 설정 (주피터 노트북의 파라미터 튜닝 셀 역할)
st.sidebar.header("⚙️ 분석 파라미터 설정")

# 캘리브레이션 방식 선택
calibration_method = st.sidebar.radio(
    "캘리브레이션 기준 선택",
    ("1픽셀당 실제 길이(mm) 직접 입력", "사진 촬영 가로 폭(mm) 기준 자동 계산")
)

if calibration_method == "1픽셀당 실제 길이(mm) 직접 입력":
    px_to_mm_ratio = st.sidebar.number_input(
        "1 픽셀의 물리적 크기 (mm/px)", 
        min_value=0.001, max_value=10.000, value=0.100, step=0.010, format="%.3f"
    )
else:
    real_width_mm = st.sidebar.number_input(
        "촬영된 영역의 실제 가로 길이 (mm)", 
        min_value=10.0, max_value=10000.0, value=500.0, step=10.0
    )
    px_to_mm_ratio = 1.0 # 아래 이미지 로드 시 실제 해상도 기반으로 재계산됩니다.

# 허용 균열 폭 기준 설정 (보통 콘크리트 내구성 기준 등에 따라 0.3mm 등으로 설정)
safety_threshold = st.sidebar.slider(
    "허용 균열 폭 기준 (mm)", 
    min_value=0.1, max_value=1.0, value=0.3, step=0.05
)

uploaded_file = st.file_uploader("검사할 콘크리트 표면 이미지를 업로드하세요", type=['jpg', 'png', 'jpeg'])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    image_np = np.array(image)
    image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
    
    # 가로 길이 기준으로 선택했을 경우 비율 재계산
    if calibration_method == "사진 촬영 가로 폭(mm) 기준 자동 계산":
        img_width_px = image_bgr.shape[1]
        px_to_mm_ratio = real_width_mm / img_width_px
        st.sidebar.info(f"계산된 변환 비율: 1 px ≒ {px_to_mm_ratio:.4f} mm")

    st.markdown("---")
    
    with st.spinner("알고리즘 연산 중..."):
        # 분석 실행
        binary_mask, result_bgr, df_cracks = analyze_cracks_with_scale(image_bgr, px_to_mm_ratio, safety_threshold)
        result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
        
        # [Cell 1] 전처리 마스크 확인
        st.subheader("Step 1. 균열 마스크 추출 (이진화)")
        col1, col2 = st.columns(2)
        with col1:
            st.image(image, caption="1. 원본 이미지", use_column_width=True)
        with col2:
            st.image(binary_mask, caption="2. 노이즈가 제거된 균열 영역 (이진 마스크)", use_column_width=True, channels="GRAY")
            
        st.markdown("---")
        
        # [Cell 2] 검출 결과 및 판정 시각화
        st.subheader("Step 2. 치수 측정 및 허용 기준 평가 결과")
        st.markdown(f"**허용 균열 폭 기준:** `{safety_threshold} mm` (구조물 사용성 및 내구성 검토용 기준)")
        st.image(result_rgb, caption=f"감지된 유의미한 균열: {len(df_cracks)}개 (녹색: 허용 이하, 적색: 기준 초과)", use_column_width=True)
        
        st.markdown("---")
        
        # [Cell 3] 정량적 수치 데이터베이스 및 엑셀 내보내기
        st.subheader("Step 3. 정량 분석 데이터 시트")
        if not df_cracks.empty:
            # 안전/초과 건수 요약 표시
            over_limit_count = len(df_cracks[df_cracks["상태 분류"].str.contains("초과")])
            st.metric(label="⚠️ 구조 안전성 검토 대상 균열 개수", value=f"{over_limit_count} 개 / 전체 {len(df_cracks)} 개")
            
            # 결과 표 출력
            st.dataframe(df_cracks, use_container_width=True)
            
            # Excel 다운로드 버퍼링
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_cracks.to_excel(writer, sheet_name='Crack_Inspection_Report', index=False)
            
            st.download_button(
                label="📊 정량 분석 데이터 엑셀(.xlsx) 파일 다운로드",
                data=buffer.getvalue(),
                file_name="concrete_crack_report.xlsx",
                mime="application/vnd.ms-excel"
            )
        else:
            st.success("해당 부재 표면에서 검출 조건(50px 이상)을 만족하는 유의미한 균열이 발견되지 않았습니다.")