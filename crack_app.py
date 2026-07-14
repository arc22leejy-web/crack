import streamlit as st
import streamlit.components.v1 as components

# 1. Streamlit 기본 페이지 설정
st.set_page_config(
    page_title="ROAD CRACK AI - 안전진단 시스템",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. 분석 엔진이 포함된 HTML/JS 소스코드
html_code = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ROAD CRACK AI</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Noto+Sans+KR:wght@400;700&display=swap');
        body { font-family: 'Inter', 'Noto Sans KR', sans-serif; }
        .canvas-container canvas { max-width: 100%; height: auto; border-radius: 6px; }
    </style>
</head>
<body class="bg-slate-950 text-slate-100 pb-12">
    <header class="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 py-4 flex flex-col sm:flex-row justify-between items-center gap-4">
            <div class="flex items-center gap-3">
                <div class="p-2 bg-blue-600 rounded-lg text-white"><i data-lucide="activity" class="w-6 h-6"></i></div>
                <div>
                    <h1 class="text-xl font-bold tracking-tight text-white flex items-center gap-2">
                        ROAD CRACK AI <span class="text-xs bg-blue-500/20 text-blue-400 font-normal px-2 py-0.5 rounded-full border border-blue-500/30">Streamlit v1.0</span>
                    </h1>
                    <p class="text-xs text-slate-400">지능형 콘크리트 노면 표면 분석 및 실시간 안전진단 도구</p>
                </div>
            </div>
            <div class="flex items-center gap-2">
                <button id="btnGenerateSample" class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium rounded-lg transition-colors flex items-center gap-2 border border-slate-700">
                    <i data-lucide="sparkles" class="w-4 h-4 text-amber-400"></i> 샘플 도로 생성
                </button>
                <label for="imageUpload" class="cursor-pointer px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-lg transition-colors flex items-center gap-2">
                    <i data-lucide="upload" class="w-4 h-4"></i> 사진 업로드
                </label>
                <input type="file" id="imageUpload" accept="image/*" class="hidden">
            </div>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 mt-8">
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
            <div class="lg:col-span-4 space-y-6">
                <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
                    <h2 class="text-sm font-bold uppercase tracking-wider text-slate-400 mb-4 flex items-center gap-2">
                        <i data-lucide="shield-alert" class="w-4 h-4 text-blue-500"></i> AI 진단 시스템 판정
                    </h2>
                    <div id="statusCard" class="p-4 rounded-lg border flex items-start gap-3 transition-all duration-300 bg-emerald-500/10 border-emerald-500/30 text-emerald-400">
                        <div id="statusIconContainer" class="p-2 bg-emerald-500/20 rounded-md"><i id="statusIcon" data-lucide="check-circle" class="w-5 h-5"></i></div>
                        <div>
                            <h3 id="statusTitle" class="font-bold text-sm">대기 중...</h3>
                            <p id="statusDesc" class="text-xs text-slate-400 mt-1">상단의 샘플 도로 생성을 누르거나 노면 균열 이미지를 업로드해 주세요.</p>
                        </div>
                    </div>
                    <div class="grid grid-cols-2 gap-4 mt-5">
                        <div class="bg-slate-950 p-3 rounded-lg border border-slate-800/80">
                            <span class="text-[10px] text-slate-500 block uppercase font-bold">균열 점유율</span>
                            <span id="txtCrackRatio" class="text-xl font-bold text-slate-200 mt-1 block">0.000%</span>
                        </div>
                        <div class="bg-slate-950 p-3 rounded-lg border border-slate-800/80">
                            <span class="text-[10px] text-slate-500 block uppercase font-bold">검출된 균열 구역</span>
                            <span id="txtCrackCount" class="text-xl font-bold text-slate-200 mt-1 block">0개</span>
                        </div>
                    </div>
                </div>

                <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl space-y-5">
                    <h2 class="text-sm font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                        <i data-lucide="sliders" class="w-4 h-4 text-blue-500"></i> 실시간 비전 조정 필터
                    </h2>
                    <div class="space-y-2">
                        <div class="flex justify-between items-center text-xs">
                            <label class="text-slate-300 font-medium flex items-center gap-1.5"><span class="w-1.5 h-1.5 rounded-full bg-blue-500"></span> 검출 민감도 (Threshold)</label>
                            <span id="valThresh" class="font-mono text-blue-400 font-bold bg-blue-500/10 px-1.5 py-0.5 rounded">15</span>
                        </div>
                        <input type="range" id="slideThresh" min="5" max="60" value="15" class="w-full accent-blue-500 bg-slate-950 h-2 rounded-lg appearance-none cursor-pointer">
                    </div>
                    <div class="space-y-2">
                        <div class="flex justify-between items-center text-xs">
                            <label class="text-slate-300 font-medium flex items-center gap-1.5"><span class="w-1.5 h-1.5 rounded-full bg-violet-500"></span> 미세 노이즈 필터 (Min Area)</label>
                            <span id="valMinArea" class="font-mono text-violet-400 font-bold bg-violet-500/10 px-1.5 py-0.5 rounded">15px</span>
                        </div>
                        <input type="range" id="slideMinArea" min="2" max="150" value="15" class="w-full accent-violet-500 bg-slate-950 h-2 rounded-lg appearance-none cursor-pointer">
                    </div>
                    <div class="space-y-2">
                        <div class="flex justify-between items-center text-xs">
                            <label class="text-slate-300 font-medium flex items-center gap-1.5"><span class="w-1.5 h-1.5 rounded-full bg-rose-500"></span> 위험 판정 기준치 (%)</label>
                            <span id="valDecisionLimit" class="font-mono text-rose-400 font-bold bg-rose-500/10 px-1.5 py-0.5 rounded">0.030%</span>
                        </div>
                        <input type="range" id="slideDecisionLimit" min="0.005" max="0.5" step="0.005" value="0.030" class="w-full accent-rose-500 bg-slate-950 h-2 rounded-lg appearance-none cursor-pointer">
                    </div>
                </div>

                <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl space-y-3">
                    <h2 class="text-sm font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                        <i data-lucide="folder-archive" class="w-4 h-4 text-blue-500"></i> 제출용 파일 저장
                    </h2>
                    <p class="text-xs text-slate-500 leading-relaxed">버튼을 클릭해 분석 데이터를 로컬에 즉시 파일로 내보냅니다.</p>
                    <div class="grid grid-cols-2 gap-3 pt-2">
                        <button id="btnDownloadInput" class="px-3 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-lg border border-slate-700/80 flex items-center justify-center gap-1.5">
                            <i data-lucide="download" class="w-3.5 h-3.5 text-blue-400"></i> 원본 (input.png)
                        </button>
                        <button id="btnDownloadOutput" class="px-3 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-lg border border-slate-700/80 flex items-center justify-center gap-1.5">
                            <i data-lucide="download" class="w-3.5 h-3.5 text-emerald-400"></i> 가공 (output.png)
                        </button>
                    </div>
                </div>
            </div>

            <div class="lg:col-span-8 space-y-6">
                <div id="dropZone" class="border-2 border-dashed border-slate-800 hover:border-blue-500/50 bg-slate-900/40 hover:bg-slate-900/60 transition-all rounded-xl p-6 text-center cursor-pointer flex flex-col items-center justify-center gap-3">
                    <div class="w-12 h-12 rounded-full bg-slate-800 flex items-center justify-center text-slate-400 border border-slate-700/60"><i data-lucide="image" class="w-6 h-6 text-blue-400"></i></div>
                    <div>
                        <p class="text-sm font-semibold text-slate-300">이곳에 분석할 노면 사진을 끌어다 놓으세요</p>
                        <p class="text-xs text-slate-500 mt-1">PNG, JPG 형식 지원</p>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl flex flex-col">
                        <div class="flex justify-between items-center mb-3">
                            <span class="text-xs font-bold text-slate-400 uppercase tracking-wide flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-rose-500"></span> Original & AI Box</span>
                            <span class="text-[10px] bg-slate-800 px-2 py-0.5 rounded text-slate-400" id="txtInputName">가상 콘크리트 노면</span>
                        </div>
                        <div class="canvas-container bg-slate-950 rounded border border-slate-800/60 p-2 flex items-center justify-center min-h-[300px]"><canvas id="canvasOriginal"></canvas></div>
                    </div>
                    <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl flex flex-col">
                        <div class="flex justify-between items-center mb-3">
                            <span class="text-xs font-bold text-slate-400 uppercase tracking-wide flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-slate-400"></span> Extracted Binary Mask</span>
                            <span class="text-[10px] bg-slate-800 px-2 py-0.5 rounded text-slate-400">이진화 균열 마스크</span>
                        </div>
                        <div class="canvas-container bg-slate-950 rounded border border-slate-800/60 p-2 flex items-center justify-center min-h-[300px]"><canvas id="canvasMask"></canvas></div>
                    </div>
                </div>
            </div>
        </div>
    </main>
    <canvas id="canvasHidden" class="hidden"></canvas>

    <script>
        const imageUpload = document.getElementById('imageUpload');
        const dropZone = document.getElementById('dropZone');
        const btnGenerateSample = document.getElementById('btnGenerateSample');
        const btnDownloadInput = document.getElementById('btnDownloadInput');
        const btnDownloadOutput = document.getElementById('btnDownloadOutput');
        const canvasOriginal = document.getElementById('canvasOriginal');
        const canvasMask = document.getElementById('canvasMask');
        const canvasHidden = document.getElementById('canvasHidden');
        const slideThresh = document.getElementById('slideThresh');
        const slideMinArea = document.getElementById('slideMinArea');
        const slideDecisionLimit = document.getElementById('slideDecisionLimit');
        const valThresh = document.getElementById('valThresh');
        const valMinArea = document.getElementById('valMinArea');
        const valDecisionLimit = document.getElementById('valDecisionLimit');
        const txtCrackRatio = document.getElementById('txtCrackRatio');
        const txtCrackCount = document.getElementById('txtCrackCount');
        const txtInputName = document.getElementById('txtInputName');
        const statusCard = document.getElementById('statusCard');
        const statusIconContainer = document.getElementById('statusIconContainer');
        const statusIcon = document.getElementById('statusIcon');
        const statusTitle = document.getElementById('statusTitle');
        const statusDesc = document.getElementById('statusDesc');

        let uploadedImageSource = null;
        lucide.createIcons();

        slideThresh.addEventListener('input', (e) => { valThresh.textContent = e.target.value; processImage(); });
        slideMinArea.addEventListener('input', (e) => { valMinArea.textContent = e.target.value + 'px'; processImage(); });
        slideDecisionLimit.addEventListener('input', (e) => { valDecisionLimit.textContent = parseFloat(e.target.value).toFixed(3) + '%'; processImage(); });

        imageUpload.addEventListener('change', handleFileSelect);
        dropZone.addEventListener('click', () => imageUpload.click());
        dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('border-blue-500'); });
        dropZone.addEventListener('dragleave', () => dropZone.classList.remove('border-blue-500'));
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('border-blue-500');
            if (e.dataTransfer.files.length > 0) loadImageFromFile(e.dataTransfer.files[0]);
        });

        btnDownloadInput.addEventListener('click', () => { if (uploadedImageSource) downloadCanvasAsPng(canvasOriginal, 'input.png'); });
        btnDownloadOutput.addEventListener('click', () => { if (uploadedImageSource) downloadCanvasAsPng(canvasMask, 'output.png'); });
        btnGenerateSample.addEventListener('click', generateSampleConcreteWithCracks);

        function handleFileSelect(e) { if (e.target.files.length > 0) loadImageFromFile(e.target.files[0]); }
        function loadImageFromFile(file) {
            const reader = new FileReader();
            reader.onload = function(event) {
                const img = new Image();
                img.onload = function() { uploadedImageSource = img; txtInputName.textContent = file.name; processImage(); };
                img.src = event.target.result;
            };
            reader.readAsDataURL(file);
        }

        function generateSampleConcreteWithCracks() {
            const w = 550, h = 400;
            canvasHidden.width = w; canvasHidden.height = h;
            const ctx = canvasHidden.getContext('2d');
            ctx.fillStyle = '#94a3b8'; ctx.fillRect(0, 0, w, h);

            const imgData = ctx.getImageData(0, 0, w, h);
            const data = imgData.data;
            for (let i = 0; i < data.length; i += 4) {
                const noise = (Math.random() - 0.5) * 52;
                data[i] = Math.min(255, Math.max(0, data[i] + noise));
                data[i+1] = Math.min(255, Math.max(0, data[i+1] + noise));
                data[i+2] = Math.min(255, Math.max(0, data[i+2] + noise));
            }
            ctx.putImageData(imgData, 0, 0);

            ctx.strokeStyle = '#1e293b'; ctx.lineWidth = 2.5; ctx.lineJoin = 'round'; ctx.lineCap = 'round';
            ctx.beginPath();
            let cx = 150 + Math.random() * 200, cy = 0;
            ctx.moveTo(cx, cy);
            while (cy < h) { cy += 12 + Math.random() * 15; cx += (Math.random() - 0.5) * 22; ctx.lineTo(cx, cy); }
            ctx.stroke();

            ctx.lineWidth = 1.2; ctx.beginPath(); ctx.moveTo(cx - 30, cy - 180);
            ctx.lineTo(cx - 50 + (Math.random() - 0.5)*15, cy - 130);
            ctx.lineTo(cx - 80 + (Math.random() - 0.5)*15, cy - 80);
            ctx.stroke();

            const sampleImg = new Image();
            sampleImg.onload = function() { uploadedImageSource = sampleImg; txtInputName.textContent = 'sample_pavement_crack.png'; processImage(); };
            sampleImg.src = canvasHidden.toDataURL();
        }

        function processImage() {
            if (!uploadedImageSource) return;
            const maxDimension = 600;
            let w = uploadedImageSource.width, h = uploadedImageSource.height;
            if (w > maxDimension || h > maxDimension) {
                if (w > h) { h = Math.round((h * maxDimension) / w); w = maxDimension; }
                else { w = Math.round((w * maxDimension) / h); h = maxDimension; }
            }
            canvasHidden.width = w; canvasHidden.height = h;
            const ctxHidden = canvasHidden.getContext('2d');
            ctxHidden.drawImage(uploadedImageSource, 0, 0, w, h);

            const imgData = ctxHidden.getImageData(0, 0, w, h);
            const pixels = imgData.data;
            const gray = new Uint8ClampedArray(w * h);
            for (let i = 0; i < pixels.length; i += 4) {
                gray[i/4] = Math.round(0.299*pixels[i] + 0.587*pixels[i+1] + 0.114*pixels[i+2]);
            }

            const radius = 7;
            const blur = new Uint8ClampedArray(w * h);
            for (let y = 0; y < h; y++) {
                for (let x = 0; x < w; x++) {
                    let sum = 0, count = 0;
                    for (let dx = -radius; dx <= radius; dx++) {
                        const nx = x + dx;
                        if (nx >= 0 && nx < w) { sum += gray[y * w + nx]; count++; }
                    }
                    blur[y * w + x] = sum / count;
                }
            }

            const blackhat = new Uint8ClampedArray(w * h);
            for (let x = 0; x < w; x++) {
                for (let y = 0; y < h; y++) {
                    let sum = 0, count = 0;
                    for (let dy = -radius; dy <= radius; dy++) {
                        const ny = y + dy;
                        if (ny >= 0 && ny < h) { sum += blur[ny * w + x]; count++; }
                    }
                    blackhat[y * w + x] = Math.max(0, (sum / count) - gray[y * w + x]);
                }
            }

            const threshVal = parseInt(slideThresh.value);
            const binary = new Uint8ClampedArray(w * h);
            for (let i = 0; i < w*h; i++) binary[i] = (blackhat[i] > threshVal) ? 255 : 0;

            const minAreaVal = parseInt(slideMinArea.value);
            const visited = new Uint8Array(w * h);
            const detectedCracks = [];
            let totalCrackPixels = 0;

            for (let y = 0; y < h; y++) {
                for (let x = 0; x < w; x++) {
                    const idx = y * w + x;
                    if (binary[idx] === 255 && !visited[idx]) {
                        const queue = [idx]; visited[idx] = 1;
                        let minX = x, maxX = x, minY = y, maxY = y, count = 0, head = 0;
                        while (head < queue.length) {
                            const curr = queue[head++]; count++;
                            const cy = Math.floor(curr / w), cx = curr % w;
                            const neighbors = [{cx: cx+1, cy: cy}, {cx: cx-1, cy: cy}, {cx: cx, cy: cy+1}, {cx: cx, cy: cy-1}];
                            for (const n of neighbors) {
                                if (n.cx >= 0 && n.cx < w && n.cy >= 0 && n.cy < h) {
                                    const nidx = n.cy * w + n.cx;
                                    if (binary[nidx] === 255 && !visited[nidx]) {
                                        visited[nidx] = 1; queue.push(nidx);
                                        if (n.cx < minX) minX = n.cx; if (n.cx > maxX) maxX = n.cx;
                                        if (n.cy < minY) minY = n.cy; if (n.cy > maxY) maxY = n.cy;
                                    }
                                }
                            }
                        }
                        if (count >= minAreaVal) {
                            detectedCracks.push({ x: minX, y: minY, w: maxX - minX + 1, h: maxY - minY + 1, area: count });
                            totalCrackPixels += count;
                        } else {
                            for (let k = 0; k < queue.length; k++) binary[queue[k]] = 0;
                        }
                    }
                }
            }

            canvasOriginal.width = w; canvasOriginal.height = h;
            const ctxOrig = canvasOriginal.getContext('2d'); ctxOrig.drawImage(uploadedImageSource, 0, 0, w, h);
            ctxOrig.strokeStyle = '#ef4444'; ctxOrig.lineWidth = 2.5;
            for (const r of detectedCracks) ctxOrig.strokeRect(r.x, r.y, r.w, r.h);

            canvasMask.width = w; canvasMask.height = h;
            const ctxMask = canvasMask.getContext('2d');
            const maskImgData = ctxMask.createImageData(w, h);
            const maskPixels = maskImgData.data;
            for (let i = 0; i < w*h; i++) {
                const val = binary[i];
                maskPixels[i*4] = val; maskPixels[i*4+1] = val; maskPixels[i*4+2] = val; maskPixels[i*4+3] = 255;
            }
            ctxMask.putImageData(maskImgData, 0, 0);

            const totalPixels = w * h;
            const crackRatio = (totalCrackPixels / totalPixels) * 100;
            const decisionLimitVal = parseFloat(slideDecisionLimit.value);

            txtCrackRatio.textContent = crackRatio.toFixed(3) + '%';
            txtCrackCount.textContent = detectedCracks.length + '개';
            updateStatusCard(crackRatio >= decisionLimitVal, crackRatio, decisionLimitVal, detectedCracks.length);
        }

        function updateStatusCard(hasCrack, ratio, limit, count) {
            if (hasCrack) {
                statusCard.className = "p-4 rounded-lg border flex items-start gap-3 bg-rose-500/10 border-rose-500/30 text-rose-400";
                statusIconContainer.className = "p-2 bg-rose-500/20 rounded-md text-rose-400";
                statusIcon.setAttribute('data-lucide', 'alert-triangle');
                statusTitle.textContent = "🚨 위험: 노면 균열 감지됨!";
                statusDesc.textContent = `균열 점유율(${ratio.toFixed(3)}%)이 판정 기준(${limit.toFixed(3)}%)을 초과했습니다. 결함 수: ${count}개`;
            } else {
                statusCard.className = "p-4 rounded-lg border flex items-start gap-3 bg-emerald-500/10 border-emerald-500/30 text-emerald-400";
                statusIconContainer.className = "p-2 bg-emerald-500/20 rounded-md text-emerald-400";
                statusIcon.setAttribute('data-lucide', 'check-circle');
                statusTitle.textContent = "✅ 양호: 도로 노면 상태 안전";
                statusDesc.textContent = `누적 면적 비율(${ratio.toFixed(3)}%)이 안정 범위 내에 유지 중입니다.`;
            }
            lucide.createIcons();
        }

        function downloadCanvasAsPng(canvas, filename) {
            const link = document.createElement('a'); link.download = filename;
            link.href = canvas.toDataURL('image/png'); link.click();
        }

        window.onload = function() { generateSampleConcreteWithCracks(); };
    </script>
</body>
</html>
"""

# 3. Streamlit 앱 화면에 HTML 컴포넌트를 렌더링
components.html(html_code, height=980, scrolling=True)