# 安裝步驟
## 環境準備
* 下載此repo與靜態檔案
```
git clone https://github.com/CTingy/sttmountain.git --recurse-submodules
```
* python3 與建立虛擬環境
```
sudo apt-get install python3.7
python3 -m venv <myenvname>
```
* 進入虛擬環境安裝套件
```
source <myenvname>/bin/activate
pip install -r requirements.txt
```
* 資料庫
```
docker pull mongo:4.2.6
docker pull redis
```
* mongo 建立使用者帳號密碼
([參考此](https://stackoverflow.com/questions/37450871/how-to-allow-remote-connections-from-mongo-docker-container))
進入docker
```
docker run -d -p 27017:27017 -v ~/dataMongo:/data/db mongo
docker ps
docker exec -it <mongo_contianer_id> bash
```
進入後
```
mongo
> use <your_db_name>
> db.createUser({
    user: '<mongo_user_name>',
    pwd: '<secret_password>',
    roles: [{ role: 'readWrite', db:'<your_db_name>'}]
})
```
離開docker，使用密碼模式重新啟動
```
docker stop <mongo_container_id>
docker run -d -p 27017:27017 -v ~/dataMongo:/data/db mongo mongod --auth
```
## 所需環境變數
* 可將此寫入虛擬環境啟動用的active之中
```shell
# environment variable for 專案根目錄
export SECRET_KEY=自己隨便打一個
export FLASK_ENV=development
export DB_NAME=上面doker之中建立的your_db_name
export DB_USERNAME=上面doker之中建立的mongo_user_name
export DB_PASSWORD=上面doker之中建立的secret_password
export DB_HOST=127.0.0.1
export DB_PORT=27017
export DB_NAME=上面doker之中建立的db_name

# google service
# 此為goole第三方登入使用，不需要此功能的話這邊不用寫
export GOOGLE_CLIENT_ID=自己申請一個
export GOOGLE_CLIENT_SECRET=自己申請一個

# mail server
export DEV_MAIL_USERNAME=參見下方指定smtp server章節
export DEV_MAIL_PASSWORD=參見下方指定smtp server章節

# google drive api
# 此為至goole drive產生人員名冊用，不需要此功能的話這邊不用寫
export GOOGLE_DRIVE_FOLDER_ID=自己申請一個
export GOOGLE_DRIVE_API_CERD_PATH=自己申請一個
```
## 指定smtp server
下面示範使用mailtrap的步驟
* 至https://mailtrap.io/ 申請一個帳號
* 登入後至https://mailtrap.io/inboxes/ ，點選Action欄位的齒輪
* 進入後下方Integrations選擇Flask-Mail
* 複製訊息框中的`MAIL_USERNAME`與`MAIL_PASSWORD`

至虛擬環境中，新增環境變數：
```
export DEV_MAIL_USERNAME=剛剛複製的username
export DEV_MAIL_PASSWORD=剛剛複製的password
```
若不使用mailtrap，自行至`專案根目錄/config.py`中修改以下程式碼：
```python
class DevelopmentConfig(Config):
    MAIL_SERVER = 'smtp.mailtrap.io'
    MAIL_PORT = 2525
    MAIL_USERNAME = os.environ.get('DEV_MAIL_USERNAME', None)
    MAIL_PASSWORD = os.environ.get('DEV_MAIL_PASSWORD', None)
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
```

## 加入靜態檔案
* 若是一開始clone此專案時未下載到submodule靜態檔的話，請執行：
```
git submodule update --init
```
* 最後專案結構會變成像是這樣：
```
- 專案根目錄/
    - static/
    - sttapp/
        - auth/
        - users/
        - proposals/
        - events/ 
        - ....
    - README.md
    - requirements.txt
```
* 更多submodule設定使用[參考](https://blog.puckwang.com/post/2020/git-submodule-vs-subtree/)

# 啟動
```
cd 專案根目錄/sttapp/
flask run
```
按 ctrl+c 離開

# 建立第一個登入者
* 請先建立第一位使用者，才使用邀請功能讓其他帳號註冊
* 其實也是因為此網站不登入的話幾乎沒剩下什麼功能可以用@@  
* 詳細登入功能請見下方的註冊與登入
```
cd 專案根目錄/sttapp/
flask shell
```
在shell之中：
```python
from sttapp.users.models import SttUser
user = SttUser()
user.username = "<網站顯示名稱>"
user.email = "<email>"
user.password = "<輸入密碼>"  # 請直接輸入密碼，資料庫會hash後再儲存
user.save()
```

# 功能說明
## 註冊與登入
* 由一個已登入者使用邀請功能，填入被邀請人信箱
* 被邀請人的信箱收到邀請註冊的連結
* 被邀請人點選連結來到註冊頁面
* 選擇註冊方式：
    * 使用信箱（系統將使用邀請信寄送信箱）
    * 使用google帳號（系統使用該google帳號之gmail信箱）
    * 使用facebook帳號（目前未開放）
* 填寫註冊表單，僅使用信箱註冊者需輸入密碼
* 登入方式：
    * 僅使用信箱註冊者需用**邀請信信箱 + 密碼**登入網站
    * 使用google/facebook使用者僅需在登入頁面點選登入方式即可

## 不登入功能
* 出隊文標題、內文搜尋
* 檢視所有出隊文

## 登入後功能
登入後，可跑整個出隊流程，簡述如下：
### 出隊用人員資料
* 新增/修改/刪除
* 使用身分證字號+姓名搜尋人員資料
* 可查看該出隊人員資料過往出隊文歷史（當然是從系統建置之後開始算）
### 企劃書
* 使用"我要開隊"按鈕，會新建立一份企劃書（包含出隊文基本資料、預計行程、人員資料動態搜索）
* 僅建立者可編輯、刪除
* 僅建立者可檢視詳細人員資料
* 僅建立者可操作產生出隊人員資料表，按下產生按鈕可至山協G suite建立入山人員名冊、直企格式人員名冊（整張直企太複雜啦，先有人員資料就好，完整版再等等）
* 所有登入者皆可檢視所有企劃書
* 所有登入者皆可將此企劃書發佈為出隊文（出隊文不須登入即可看見）
* 建立者的個人頁面超連結
* 出隊成員的個人頁面超連結（若該出隊用資料與使用者已連結的話，請見**使用者頁面**章節）

### 出隊文
* 發佈時填寫集合時間、地點後產生出隊文
* 出隊文在回報下山以前無法直接編輯，所有編輯行為皆為編輯該出隊文之企劃書（故此權限與企劃書編輯相同）
* 發佈者回報該出隊文為：**已下山**，並且輸入實際行程與心得
    * 回報已下山的同時，該隊伍下出隊成員若擁有網站帳號，系統會其出隊文資料寫入該帳號下的**個人出隊歷史**之中（詳見下方**使用者頁面**章節）
* 或是發佈者回報為**已撤退**
* 回報已下山之出隊文，發佈者可編輯實際行程與出隊心得
    * 注意，此時若更改實際行程天數，將無法同步至上述個人出隊歷史之中
* 該出隊文發佈者可在回報下山與撤退以前刪除此出隊文，並可重新使用企劃書發佈功能產生新的出隊文
* 回報已下山或是撤退之出隊文不可刪除與編輯該出隊文之企劃書
* 建立者的個人頁面超連結
* 出隊成員的個人頁面超連結（若該出隊用資料與使用者已連結的話，請見**使用者頁面**章節）

### 邀請功能
* 詳見上方**新帳號註冊流程**
### 我要開隊功能
* 詳見上方**企劃書**章節

### 使用者頁面
* 個人基本資料頁（所有登入者可檢視）
* 個人站內出隊文紀錄（僅已匯入出隊資料的人有該頁面、此頁面所有登入者可檢視）
* 個人進階資料頁（僅資料所有者可檢視）
* 個人出隊資料頁（僅資料所有者可檢視）
    * 若該使用者未連結其出隊用資料，則可使用**身份證+手機**來匯入該員於站內的出隊用資料
    * 若找不到上述資料，則需先建立新的個人出隊用資料後，再執行匯入功能（系統會幫忙填寫與網站帳號的共同欄位部份）
* 個人出隊歷史（所有登入者可檢視）
    * 所有者可新增/修改/刪除，也可隨意改動出隊歷史順序
    * 此為個人維護區塊，重點為紀錄自己的點滴，也歡迎填寫校外出隊經驗
    * 若有連結出隊資料，站內出隊紀錄系統會於出隊文回報下山時（詳見上方**出隊文**一節）自動寫入至此
    * 同上，但若之後出隊文內容有更動不會同步改動於此。
* 個人PO文紀錄（目前僅囊括出隊文、企劃書）

# 近期計畫
這邊列出幾個重要、優先度高、但尚未完成之功能（包含系統面與商業邏輯），會接著優先開發這些
* view function的單元測試
* 加入CI
* 直企＆出隊文回文資料補齊
* 圖文編輯功能
* 文章評論功能
* 權限控管
* 全文檢索
* 文章上標籤、標籤分類
