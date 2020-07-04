# 安裝步驟
## 下載
* clone with https
```
git clone https://github.com/CTingy/sttmountain.git --recurse-submodules
```
* clone with SSH
```
git clone git@github.com:CTingy/sttmountain.git --recurse-submodules
```
* 若是一開始clone此專案時未下載到submodule靜態檔的話，請執行：
```
git submodule update --init
```
## 安裝與運行

### 環境變數
* 在專案跟目錄新增`.env`檔案如下，並填上空白處
* `DEV_MAIL_USERNAME`與`DEV_MAIL_PASSWORD`使用方式可參考下方的：指定smtp server
```
SECRET_KEY=
FLASK_APP=sttapp/app.py
FLASK_ENV=development
DB_NAME=
DB_USERNAME=
DB_PASSWORD=
DB_PORT=27017
DB_NAME=

# google相關功能未使用可留白
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_DRIVE_FOLDER_ID=
GOOGLE_DRIVE_API_CERD_PATH=

DEV_MAIL_USERNAME=
DEV_MAIL_PASSWORD=
MAIL_DEFAULT_SENDER=
ADMIN_EMAIL=
```

### 指定smtp server
下面示範使用mailtrap的步驟
* 至https://mailtrap.io/ 申請一個帳號
* 登入後至https://mailtrap.io/inboxes/ ，點選Action欄位的齒輪
* 進入後下方Integrations選擇Flask-Mail
* 複製訊息框中的`MAIL_USERNAME`與`MAIL_PASSWORD`

至`.env`檔案中，新增環境變數：
```
DEV_MAIL_USERNAME=剛剛複製的username
DEV_MAIL_PASSWORD=剛剛複製的password
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
### 跑起來～
* 安裝docker、docker-compose
```
cd 專案根目錄/
docker-compose rm -fs
docker-compose build
docker-compose up
```
### 充填初始資料

### 補充資料
* mongo container 建立使用者帳號密碼
([參考此](https://stackoverflow.com/questions/37450871/how-to-allow-remote-connections-from-mongo-docker-container))
* 更多submodule設定使用[參考](https://blog.puckwang.com/post/2020/git-submodule-vs-subtree/)

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
