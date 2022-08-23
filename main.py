from os import name
import pymongo
import gridfs
from flask import send_file

myclient=pymongo.MongoClient('mongodb://localhost:27017/')
mydb=myclient['amansac']
mycol=mydb['test_col']
from datetime import datetime
from flask import Flask,request
app = Flask(__name__)

"""
query parameter - ?name=Aman&age=19 --> request.args.get('nm')
path parameter - /login/<name>/<age> --> function(name, age)
body - 
    form paramter - postman --> body --> form data - request.form['nm']
    json - {     --> request.get_json()
        "name": "Aman",
        "Age": 19
    }
"""
@app.route('/upload_song',methods=['POST'])
def upload_audio_file():
    """Args: 
            name:
            album:
            artist:
            song_file:
        Return:
            return: {"status": "Song uploaded successfully.", "status_code"=200}
    """
    artist=request.form['artist']
    album=request.form['album']
    song_name=request.form['song_name']
    song_file = request.files['song_file']
    song_filestr = song_file.read()
    fs=gridfs.GridFS(mydb)
    file_id = fs.put(song_filestr, song_name=song_name, album=album, artist=artist, date_created=datetime.now())
    return {"status": "file uploaded", "status_code": 200}  

@app.route('/fetch_song',methods=['GET'])
def fetch_audio_file():
    """Args:
            name:
        Return:
            song_file:
    """
    # db.fs.files.find( { a: 1 } ).showRecordId()
    # input --> song_name
    # fetch object id from gridfs for song name.

    # fetch file corresponing to object id.
    # return/download/play the file
    song_file = request.args['song_name']
    fs=gridfs.GridFS(mydb)
    #result = fs.files.find_one({"song_name":song_file})
    result = fs.find_one( { "song_name": song_file } )
    file = fs.get(result._id)
    return send_file(
                file, attachment_filename=file.song_name+".mp3", as_attachment=True
            ) 

@app.route('/delete_song',methods=['DELETE'])
def delete_audio_file():
    """Args:
            name:
        Return:
            {"status": "Song Deleted Successfully", status_code=200}
    """
    # input --> song_name
    # fetch id from gridfs corresponding to song_name.
    # delete file from gridfs.
    song_file=request.form['song_name']
    fs=gridfs.GridFS(mydb)
    result = fs.find_one({"song_name":song_file})
    # id=None
    # for x in result :
    #     id = x['_id']
    files_id = result._id
    fs.delete(files_id)

    return {"status": "File deleted successfully", "status_code": 200}
      #  g.db.execute('delete from entries WHERE id = ?',[id])
@app.route('/update_song_info',methods=['PUT'])
def update_song_info():
    """Args:
            body: {
                "name":
                "album":
                "artist":
            }
        Return: {status: "song info updated", status_code=200}
    """
    # fetch values from body. request.get_json() --> dict.
    # update album and artist where song_name is the one we received in body.
    data = request.get_json()
    song_name = data['song_name']
    del data['song_name']

    fs=gridfs.GridFS(mydb)
    result = fs.find_one({"song_name": song_name})
    file_id = result._id
    file = fs.get(file_id)
    fs.delete(file_id)
    fs.put(file.read(), song_name=song_name, album=data['album'], artist=data["artist"], date_created=datetime.now())    
    return {"status": "File updated successfully", "status_code": 200}

if __name__=='__main__':
    app.run(debug = True)
