# generator/views.py (가장 기본적인 모델로 최종 테스트)

import os
import uuid
import google.generativeai as genai
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
#from dotenv import load_dotenv 배포때 주석
from PIL import Image
from io import BytesIO
import base64

# --- Vertex AI 라이브러리 추가 ---
import vertexai
from vertexai.generative_models import GenerativeModel, Part

# .env 파일에서 환경 변수 로드
#load_dotenv() 배포때 주석
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY가 .env 파일에 설정되지 않았습니다.")

# Gemini API 설정 (이미지 생성용)
genai.configure(api_key=api_key)

# 메인 페이지 렌더링
def index(request):
    return render(request, 'generator/index.html')

# 이미지 생성 함수 (나노바나나 - 수정 없음)
@csrf_exempt
def generate_image(request):
    if request.method == 'POST':
        prompt = request.POST.get('prompt')
        uploaded_files = request.FILES.getlist('images')

        if not prompt or not uploaded_files:
            return JsonResponse({'error': '프롬프트와 이미지를 모두 업로드해주세요.'}, status=400)

        try:
            model = genai.GenerativeModel('gemini-2.5-flash-image')
            contents = [prompt]
            for uploaded_file in uploaded_files:
                img = Image.open(uploaded_file)
                contents.append(img)

            response = model.generate_content(contents)

            generated_image_data = None
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    generated_image_data = part.inline_data.data
                    break

            if not generated_image_data:
                return JsonResponse({'error': f"API가 이미지를 생성하지 못했습니다. 응답: {response.text}"}, status=500)

            file_name = f"{uuid.uuid4()}.png"
            file_path = os.path.join(settings.MEDIA_ROOT, file_name)

            with open(file_path, "wb") as f:
                f.write(generated_image_data)

            image_url = os.path.join(settings.MEDIA_URL, file_name)
            return JsonResponse({'image_url': image_url})

        except Exception as e:
            return JsonResponse({'error': f"이미지 생성 중 서버 내부 오류: {str(e)}"}, status=500)

    return JsonResponse({'error': '잘못된 요청 방식입니다.'}, status=400)


# --- [★★★ 최종 테스트: 가장 기본적인 이미지 이해 모델 사용 ★★★] ---
@csrf_exempt
def generate_video(request):
    if request.method == 'POST':
        prompt = request.POST.get('prompt')
        image_url = request.POST.get('image_url')

        if not prompt or not image_url:
            return JsonResponse({'error': '프롬프트와 이미지가 모두 필요합니다.'}, status=400)

        try:
            # 1. Google Cloud 프로젝트 정보 설정 (새 프로젝트 ID 확인)
            PROJECT_ID = "image-475923"  # 👈 새로 만든 GCP 프로젝트 ID 확인!
            LOCATION = "us-central1"

            # Vertex AI 초기화
            vertexai.init(project=PROJECT_ID, location=LOCATION)

            # 2. 가장 기본적인 이미지+텍스트 이해 모델 지정 (영상 생성 X, 텍스트 응답 O)
            model = GenerativeModel("gemini-1.0-pro-vision") # <--- 모델 이름 변경!

            # 3. 이미지 URL을 서버의 실제 파일 경로로 변환
            image_file_path = os.path.join(settings.MEDIA_ROOT, image_url.replace(settings.MEDIA_URL, '', 1))

            if not os.path.exists(image_file_path):
                return JsonResponse({'error': '서버에서 원본 이미지 파일을 찾을 수 없습니다.'}, status=404)

            # 4. 이미지 파일을 읽어 모델이 이해하는 'Part' 객체로 변환
            with open(image_file_path, "rb") as f:
                image_data = f.read()

            mime_type = "image/png" if image_file_path.lower().endswith(".png") else "image/jpeg"
            input_image_part = Part.from_data(data=image_data, mime_type=mime_type)

            # 5. AI 모델에 [이미지, 텍스트] 순서로 요청 전송
            print(f"Vertex AI 기본 모델({model._model_name})로 텍스트 응답 생성을 요청합니다...")
            response = model.generate_content([input_image_part, prompt])

            # 6. 응답에서 영상 데이터 대신 '텍스트' 추출
            text_response = response.text # 모델이 생성한 텍스트 응답

            # 7. 프론트엔드에 영상 URL 대신 '텍스트 응답' 반환
            #    (index.html은 video_script를 받도록 이미 수정되어 있음)
            return JsonResponse({'video_script': text_response})

        except Exception as e:
            print(f"텍스트 생성 중 오류 발생: {str(e)}")
            # 오류 메시지에 모델 접근 권한 관련 내용이 있는지 확인
            error_message = f"텍스트 생성 중 서버 오류 발생: {str(e)}"
            return JsonResponse({'error': error_message}, status=500)

    return JsonResponse({'error': '잘못된 요청 방식입니다.'}, status=400)