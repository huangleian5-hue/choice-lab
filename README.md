# The Choice Lab｜消費設計觀察室（交付版）

## 核心教學知識
選擇架構（Choice Architecture）：選項的呈現、位置、提示與決策環境可能影響注意力與選擇，不保證改變每個人的購買行為。

## 兩個教學案例
- 餐廳菜單解密：先點餐，再找出推薦標示、視覺強調及排列線索。
- 日本販賣機設計師：自己調整飲料位置與推薦標示，說明選擇架構的作用及限制。

## 實際資料 ingest 範圍
`sources/catalog.json` 收錄 6 個已核對的來源入口，`sources/notes/S01–S06.md` 是根據可公開取得之**摘要／部分公開網頁內容**整理的中文研究筆記；`wiki/W01–W05.md` 是連結這些來源筆記的五個知識單元。**已匯入六份來源摘要的轉述筆記，並非六篇論文全文**。對全文有要求時須另行取得並處理原文。

## 可執行流程（本地規則式）
`python workflow.py`：讀取來源筆記→檢索 Wiki→檢查來源連結→檢查主張→檢查 HTML。

`python workflow.py --inject-bad-claim`：故意注入缺乏證據的絕對化主張，展示拒絕→修正→重新檢查的真實迴圈，最多重試兩次。

`python workflow.py --query "商品 位置" --show-retrieval`：查詢 Wiki 檢索結果。

測試輸出在 `logs/graph-normal.json`、`logs/graph-rejection.json`、`logs/retrieval-output.txt`。

**重要限制**：這是確實可執行的本地規則式 Graph／Loop；**不是 LLM API 代理，不曾呼叫 LLM 來自動撰寫或修正**。HTML 經過程式碼結構靜態檢查；未宣稱完成真實瀏覽器互動測試。

## HTML
直接打開 `index.html` 即可瀏覽 12 頁互動教學簡報；部署至 GitHub Pages 時請把此專案根目錄的 `index.html` 放在儲存庫根目錄。

## 繳交
請見 `SUBMISSION.md`，包含六項繳交內容與真實執行反思。正式繳交前需要自己部署 GitHub Pages 並補上兩個網址。
