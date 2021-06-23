import uvicorn
import json
from typing import List
from fastapi import FastAPI, Form, Body
from fastapi import Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import configparser
import webbrowser

app = FastAPI()  # app: FastAPI = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

config = configparser.ConfigParser()
config.read('config.ini')#, 'utf-8')


class DataModel(BaseModel):
    __root__: List[str]


def process_item_list(items: List[str]):
    pass


def config_update(arr, value):
    config['cfg'][arr] = str(value)
    with open('config.ini', 'w') as configfile:
        config.write(configfile)


def config_parser(i):
    arr = 'i' + str(i)
    d = dict()
    d['uslovie'] = config[arr]["uslovie"]
    d['question'] = config[arr]["question"]
    d['img1'] = config[arr]["img1"]
    d['img2'] = config[arr]["img2"]
    d['button_q1'] = config[arr]["button_q1"]
    d['button_q2'] = config[arr]["button_q2"]
    return d

config_update('i', 1)  # по умолчанию после запуска квиза счетчик вопросов становится на едниниицу
rule = 0  # по умолчанию правила нет
config_update('rule', 0)
config_update('out', '')


def end(item_id: str):
    old_out = config["cfg"]["out"]
    new_out = old_out + item_id + ";"  # все записывается подряд, потому разделитель - это ";"
    config_update('out', new_out)
    webbrowser.open('https://dodopizza.ru/peterburg#pizzas', new=0, autoraise=True)  # открыте сайта dodo


@app.get("/")  # старт кивза
async def root(request: Request):
    config_update('i', 1)  # по умолчанию после запуска квиза счетчик вопросов становится на едниниицу
    rule = 0  # по умолчанию правила нет
    config_update('rule', 0)
    config_update('out', '')  # изначально результат пустой, формируется по ходу квиза
    context = {"request": request, "rule": rule}
    return templates.TemplateResponse("start_page/index.html", context)


@app.post("/submit/")  # сохранение настроек на стартовом экране
async def root(request: Request, mr: str = Form(...)):
    config_update('rule', int(mr))
    сontext = {"request": request, "rule": int(mr)}
    return templates.TemplateResponse("start_page/index.html", сontext)


@app.post('/open_i/{item_id}')
async def root(item_id: str, request: Request):
    print(item_id)  # колбэк от шаблона
    if((item_id == '15m') or (item_id == '30m') or (item_id == '60m') or (item_id == 'no_m')):
        end(item_id)
        сontext = {"request": request}
        return templates.TemplateResponse("end_page/end_page.html", сontext)
    i = int(config["cfg"]["i"])  # получаем текущий i
    rule = config["cfg"]["rule"]
    if (int(rule) == int(i)):
        i += 1
    if (int(i) == (int(config["cfg"]["max_i"]) + 1)):
        сontext = {"request": request}
        return templates.TemplateResponse("time_page/time_page.html", сontext)
    #elif (int(i) == (int(config["cfg"]["max_i"]) + 2)):  # если то, что мы сейчас хотим отобразить отсутсвует в конфиге, завершаем квиз
    #    webbrowser.open('https://dodopizza.ru/peterburg#pizzas', new=0, autoraise=True) # открыте сайта dodo
    next_i = int(i) + 1
    config_update('i', next_i)  # записываем следующий i(i+1 по отношению к текущему, открывающемуся сейчас)
    b = config_parser(i)
    if(item_id == 'button1'):  # записываем ответ(колбэк от прошлого шаблона) в out
        old_out = config["cfg"]["out"]
        new_out = old_out + str(b['button_q1']) + ";"  # все записывается подряд, потому разделитель - это ";"
        config_update('out', new_out)
    elif(item_id == 'button2'):
        old_out = config["cfg"]["out"]
        new_out = old_out + str(b['button_q2']) + ";"
        config_update('out', new_out)
    сontext = {"request": request, 'uslovie': b["uslovie"], 'question': b['question'], 'img1': '/static/' + b['img1'], 'img2': '/static/' + b['img2'], 'button_q1': b['button_q1'], 'button_q2': b['button_q2']}
    return templates.TemplateResponse("i_page/i_page.html", сontext)

if __name__ == '__main__':
    uvicorn.run(host='0.0.0.0', port=8000, app=app)
