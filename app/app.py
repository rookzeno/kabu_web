from flask import Flask, jsonify, abort, make_response,render_template,url_for,request,redirect,send_file
import os.path
import json
import pandas as pd
from hyouka import hyouka

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024

@app.route("/")
def index():
    ranking = pd.read_csv("ranking.csv")
    ranking = ranking.groupby("name").max().sort_values("money",ascending=False)
    ranking = ranking.reset_index()
    return render_template('index.html',ranklist=ranking.values)

@app.route('/send',methods = ['post'])
def posttest():
    img_file = request.files['img_file']
    fileName = img_file.filename
    root, ext = os.path.splitext(fileName)
    name = request.form["name"]
    ext = ext.lower()
    if ext not in [".py"]:
        return render_template('index.html',massege = "対応してない拡張子です",color = "red")
    img_file.save("tmp.py")
    from tmp import myStrategy
    print("success")
    try:
        kane = int(hyouka(myStrategy))
    except:
        return render_template('index.html',massege = "解析出来ませんでした",color = "red")
    print("pf")
    ranking = pd.read_csv("ranking.csv")
    ranking = ranking.append(pd.DataFrame([[name,kane]],columns = ["name","money"]),ignore_index=True)
    ranking.to_csv("ranking.csv",index=False)
    ranking = ranking.groupby("name").max().sort_values("money",ascending=False)
    ranking = ranking.reset_index()
    rank = str(ranking[ranking.name == name].index[0] + 1) + "位"
    

    return render_template('index.html',kane=kane,rank=rank,name=name,ranklist=ranking.values)


# エラーハンドリング
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)
@app.errorhandler(503)
def all_error_handler(error):
     return 'InternalServerError\n', 503
if __name__ == '__main__':
    app.run()
