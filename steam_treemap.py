import re
import sys
import json
import requests
import operator
from bs4 import BeautifulSoup
import subprocess, os, platform
from sys import exit

def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

playerId = input("Steam id （留空则会尝试读取本目录下的content.html）: ")
thresholdInput = input("生成的游戏数量 (默认100): ")
randomOrderInput = input("随机排列? (y/n，默认n): ")

print("\n读取游戏时长...")
if(playerId==""):
    try:
        with open('content.html', 'r', encoding='utf-8') as myfile:
            page = myfile.read()
    except FileNotFoundError:
        print("错误：没有在本目录下找到content.html，请将游戏时长页面另存为成content.html并放在本目录")
        x = input("按任意键退出")
        exit()
else:
    if(isNumber(playerId)):
        url = "http://steamcommunity.com/profiles/" + playerId 
    else:
        url = "http://steamcommunity.com/id/" + playerId
    cookies = { 'birthtime': '283993201', 'mature_content': '1' }
    try:
        page = requests.get(url + "/games/?tab=all" , cookies=cookies).text
    except Exception:
        print("访问错误：请尝试关闭反代工具后使用全局魔法，或者手动访问将游戏时长页面，另存为成content.html并放在本目录")
        x = input("按任意键退出")
        exit()

threshold = 100
if isNumber(thresholdInput):
    threshold = int(thresholdInput)

sortMethod = ""
if randomOrderInput=="y":
    sortMethod = ".sort((a, b) => Math.random()-0.5)"

try:
    want = json.loads(re.search(r"var rgGames = (.*);", page).group(1))
except Exception:
    print("读取页面错误：请确认游戏时长为公开")
    x = input("按任意键退出")
    exit()

gameHourList = {}
gameImageList = {}
gameNameList = {}

count = 0
for eachJson in want:
    count = count + 1
    if count > threshold:
        break
    appId = eachJson['appid']
    if 'hours_forever' not in eachJson:
        continue
    hours = float(eachJson['hours_forever'].replace(",", ""))
    gameName = eachJson['name']
    gameHourList[appId] =  hours
    gameNameList[appId] = gameName
    gameImageList[appId] = "https://steamcdn-a.akamaihd.net/steam/apps/{}/header.jpg".format(appId)

print("\n生成页面...")
content = "<div id='viz'></div><script src='js/d3plus.full.min.js'></script><script>var data = ["

for appId, hours in gameHourList.items():
    newline = "{ name: '" + gameNameList[appId].replace("'", "\\'") + "', color: 'black', id: '" + str(appId)+  "', value: " + str(hours) + ", image: '" +gameImageList[appId] + "' },"
    content+=newline
content = content[:-1]
content += " ];new d3plus.Treemap().data(data).groupBy('name','id').duration(1000).shapeConfig({fill: function (d) {return d.color;},backgroundImage: function (d) {return d.image;},label: false,activeOpacity:1,hoverOpacity:0.8}).select('#viz').sum('value').on('click', function(d) {window.open('https://store.steampowered.com/app/' + d.id,'_blank');}).tooltipConfig({title: function(d) {return d['name'];},tbody: [['小时数', function(d) { return d['value'] }]]})" + sortMethod + ".render();</script>"
# .tile(d3.treemapSquarify.ratio(2.13))

filepath = playerId + "_treemap_output.html"
output_file = open(filepath, "w",  encoding='utf-8')
output_file.write(content)
output_file.close()

print("\n文件已保存为" + filepath + "，正在打开页面...")
if platform.system() == 'Darwin':       # macOS
    subprocess.call(('open', filepath))
elif platform.system() == 'Windows':    # Windows
    os.startfile(filepath)
else:                                   # linux variants
    subprocess.call(('xdg-open', filepath))

x = input("按任意键退出")