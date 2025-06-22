import json
import openai
import threading
import time
import queue as q
import os
import traceback
from translate import Translator

openai.api_key = 'openaikey'

def generateStyleDescription(prompt):
    messages_prompt = [
        {"role": "system", "content": "당신은 최신 패션 트렌드에 밝은 패션 스타일리스트입니다. 상황에 맞는 옷차림을 한국어로 설명해주세요."},
        {"role": "user", "content": prompt}
    ]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages_prompt,
            temperature=2.0,
            max_tokens=100
        )
        message = response["choices"][0]["message"]["content"]
        return message.strip()
    except Exception:
        print("🛑 Style GPT error:\n", traceback.format_exc())
        return "죄송합니다, 잠시 후 다시 시도해주세요."

def getImageURLFromDALLE(prompt):
    translator = Translator(from_lang='ko',to_lang='en')
    prompt = translator.translate(prompt) # prompt를 영어로 번역
    refined = (
    f"Ultra-realistic full-body fashion photo of a Korean model, "
    f"front-facing, looking directly at the camera, feet fully visible, standing naturally, "
    f"centered composition, high-resolution studio lighting, white seamless background, "
    f"sharp focus, DSLR photography, no painting, no illustration, no watercolor, "
    f"wearing an outfit described as: {prompt}, modern and trendy 2024 fashion look"
)


    response = openai.Image.create(prompt=refined,n=3,size="1024x1024") #이미지 1개 생성
    image_urls = [item['url'] for item in response['data']]
    return image_urls


def textResponseFormat(bot_response):
    return {
        'version': '2.0',
        'template': {
            'outputs': [{
                'simpleText': {'text': bot_response}
            }],
            'quickReplies': []
        }
    }

def styleResponseFormat(image_urls, style_text):
    outputs = [{'simpleText': {'text': style_text}}]
    output_text = f""" "{style_text}" 에 맞는 추천 스타일 이미지입니다! 마음에 드는 코디가 없으시다면 다시 한번 요청해주세요!"""
    for i, url in enumerate(image_urls):
        if i == len(image_urls) - 1:
            outputs.append({'simpleImage': {'imageUrl': url, 'altText': output_text}})
        else:
            outputs.append({'simpleImage': {'imageUrl': url, 'altText': ''}})
    return {
        'version': '2.0',
        'template': {
            'outputs': outputs
        }
    }


def timeover():
    return {
        'version': '2.0',
        'template': {
            'outputs': [{
                'simpleText': {
                    'text': "코디를 생성중이에요!\n30초 후 말풍선을 클릭해서 챗봇을 깨워주세요!"
                }
            }],
            'quickReplies': [{
                'action': 'message',
                'label': '자고있는 챗봇을 깨워주세요',
                'messageText': '똑똑'
            }]
        }
    }

def dbReset(filename):
    with open(filename, 'w') as f:
        f.write("")

# 실제 응답 생성 함수 (비동기 대상)
def responseOpenAI(request, response_queue, filename):
    utterance = request["userRequest"]["utterance"]
    if '똑똑' in utterance:
        try:
            with open(filename) as f:
                last_update = f.read()
            if len(last_update.split()) > 1:
                kind, *rest = last_update.split(' ', 2)
                if kind == "img":
                    image_urls_raw, prompt = rest
                    image_urls = image_urls_raw.split('|')
                    response_queue.put(styleResponseFormat(image_urls, prompt))
                else:
                    response_queue.put(textResponseFormat(" ".join(rest)))
                dbReset(filename)
        except:
            response_queue.put(textResponseFormat("기록을 불러오지 못했습니다."))
    else:
        try:
            image_urls = getImageURLFromDALLE(utterance)
            response_queue.put(styleResponseFormat(image_urls, utterance))
            with open(filename, 'w') as f:
                f.write(f"img {'|'.join(image_urls)} {utterance}")
        except:
            print("🛑 Image generation error:\n", traceback.format_exc())
            response_queue.put(textResponseFormat("이미지를 생성하지 못했습니다."))

# Lambda entry point
def lambda_handler(event, context):
    print("📦 Received event:", json.dumps(event, indent=2))  # debug log

    try:
        body = json.loads(event['body'])
    except Exception:
        print("🛑 Body parsing error:\n", traceback.format_exc())
        error_response = textResponseFormat("잘못된 요청 형식입니다.")
        return {
            'statusCode': 400,
            'body': json.dumps(error_response),
            'headers': {
                'Content-Type': 'application/json;charset=UTF-8',
                'Access-Control-Allow-Origin': '*'
            }
        }

    filename = "/tmp/botlog.txt"
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            f.write("")

    response_queue = q.Queue()
    start_time = time.time()
    response_thread = threading.Thread(target=responseOpenAI, args=(body, response_queue, filename))
    response_thread.start()

    run_flag = False
    while time.time() - start_time < 2.8:  # 카카오 timeout 감안해 3초 이내
        if not response_queue.empty():
            response = response_queue.get()
            run_flag = True
            break
        time.sleep(0.01)

    if not run_flag:
        response = timeover()

    print("📤 Response to Kakao:", json.dumps(response, indent=2))  # debug

    return {
        'statusCode': 200,
        'body': json.dumps(response),
        'headers': {
            'Content-Type': 'application/json;charset=UTF-8',
            'Access-Control-Allow-Origin': '*'
        }
    }
