#import library
import numpy as np
import joblib
from flask import Flask, render_template, request, url_for, redirect, session
from flask_admin import BaseView, expose
import pandas as pd
import flask_excel as excel
import matplotlib.pyplot as plt
import joblib
import sqlalchemy 
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'weightknn'
db = SQLAlchemy(app)

#halaman admin
admin = Admin(app,name='Prediksi Kelulusan', template_mode='bootstrap4')

#model createds
class Kelulusan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama= db.Column(db.String(50))
    umur = db.Column(db.Integer())
    jenis_kelamin = db.Column(db.String(10))
    status_sekolah = db.Column(db.String(10))
    asal_sekolah = db.Column(db.String(10))
    kegiatan_ukm = db.Column(db.String(10))
    penghasilan_ortu= db.Column(db.String(10))
    ips1= db.Column(db.Integer())
    ips2= db.Column(db.Integer())
    ips3= db.Column(db.Integer())
    ips4= db.Column(db.Integer())
    ips5= db.Column(db.Integer())
    ips6= db.Column(db.Integer())
    prediction = db.Column(db.String(100))
    pass

class multiPredict(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama= db.Column(db.String(50))
    umur = db.Column(db.Integer())
    jenis_kelamin = db.Column(db.String(10))
    status_sekolah = db.Column(db.String(10))
    asal_sekolah = db.Column(db.String(10))
    kegiatan_ukm = db.Column(db.String(10))
    penghasilan_ortu= db.Column(db.String(10))
    ips1= db.Column(db.Integer())
    ips2= db.Column(db.Integer())
    ips3= db.Column(db.Integer())
    ips4= db.Column(db.Integer())
    ips5= db.Column(db.Integer())
    ips6= db.Column(db.Integer())
    prediction = db.Column(db.String(100))
    pass

# app = Flask(__name__)
class UserView(ModelView):
        can_create = False
        can_export = True


class hasilpredik(ModelView):
    can_create = False
    can_export = True
    def is_visible(self):
        can_create = False
        can_export = True

class Rekap(BaseView):
    @expose('/')
    def index(self):
        results = Kelulusan.query.with_entities(Kelulusan.prediction).all()
        df = pd.DataFrame(results)
        df.columns = ['prediction']
        data = df.groupby('prediction').size().reset_index(name='jumlah')
        dat = pd.DataFrame(data.jumlah)
        my_labels = ['Tepat Waktu', 'Terlambat']
        my_color = ['green', 'red']
        dat.plot(kind='pie', labels=my_labels, autopct='%1.1f%%',
                 colors=my_color, subplots=True, stacked=True, legend=False)
        plt.title('Hasil Seluruh Prediksi')
        plt.xlabel('Kelulusan')
        plt.ylabel("")
        plt.savefig('static/img/hasil.png')

        # Rekap = submit()
        return self.render('admin/rekap.html')

class Multi(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/mahasiswa.html')

#Logout
class Logout(BaseView):
    @expose('/')
    def index(self):
        session.clear()
        session.pop('logged_in', None)
        return self.render('index.html')

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')

@app.route('/prediksi/', methods=['GET', 'POST'])
def prediksi():
    return render_template('form_prediksi.html')

@app.route('/mahasiswa', methods=['GET', 'POST'])
def mahasiswa():
    return render_template('mahasiswa.html')

@app.route('/admin/upload_excel', methods=['POST'])
def import_mhs():
        id=0
        db.session.query(multiPredict).delete()
        df = pd.read_excel(request.files.get('file'))
        row = pd.DataFrame(df)
        count_row = df.shape[0]

        # print(count_row)
        # print(row.iloc[0])

        for x in range(0, count_row):
            col = row.iloc[x]
            # con = mysql.connect()
            # cursor = con.cursor()

        # jenis kelamin
            if col[3] == "laki-laki":
                col3 = "0"
            else:
                col3 = "1"

        # status sekolah
            if col[4] == "negeri":
                col4 = "0"
            else:
                col4 = "1"

        # asal sekolah
            if col[5] == "sma":
                col5 = "0"
            else:
                col5 = "1"

        # kegiatan organisasi
            if col[6] == "tidak":
                col6 = "0"
            else:
                col6 = "1"

        # penghasilan ortu
            if col[7] == "tinggi":
                col7 = "2"
            elif col[7] == "sedang":
                col7 = "1"
            else:
                col7 = "0"

            prediction = preprocessDataAndPredict(col[2], col3, col4, col5, col6, col7, col[8], col[9], col[10], col[11], col[12], col[13])
            addData=multiPredict(nama=col[1], umur=int(col[2]), jenis_kelamin=col3, status_sekolah=col4, asal_sekolah=col5, kegiatan_ukm=col6, penghasilan_ortu=col7, ips1=col[8], ips2=col[9], ips3=col[10], ips4=col[11], ips5=col[12], ips6=col[13], prediction=int(prediction))
            addDataReal=Kelulusan(nama=col[1], umur=int(col[2]), jenis_kelamin=col3, status_sekolah=col4, asal_sekolah=col5, kegiatan_ukm=col6, penghasilan_ortu=col7, ips1=col[8], ips2=col[9], ips3=col[10], ips4=col[11], ips5=col[12], ips6=col[13], prediction=int(prediction))
            db.session.add(addData)
            db.session.add(addDataReal)
            db.session.commit()
        return redirect('/admin/multipredict/')

    
@app.route('/predict/', methods=['GET', 'POST'])
def predict():
    if request.method == "POST":
        # get form data
        nama = request.form.get('nama')
        umur = request.form.get('umur')
        jenis_kelamin = request.form.get('jenis_kelamin')
        status_sekolah = request.form.get('status_sekolah')
        asal_sekolah = request.form.get('asal_sekolah')
        kegiatan_ukm = request.form.get('kegiatan_ukm')
        penghasilan_ortu = request.form.get('penghasilan_ortu')
        ips1 = request.form.get('ips1')
        ips2 = request.form.get('ips2')
        ips3 = request.form.get('ips3')
        ips4 = request.form.get('ips4')
        ips5 = request.form.get('ips5')
        ips6 = request.form.get('ips6')

        
      # panggil preprocessDataAndPredict and pass inputs
        try:
            prediction = preprocessDataAndPredict(umur, jenis_kelamin,status_sekolah,asal_sekolah,kegiatan_ukm, penghasilan_ortu, ips1, ips2, ips3, ips4, ips5, ips6)
            # pass prediction to template
            predictiondb = Kelulusan(nama=nama, umur=umur, jenis_kelamin=jenis_kelamin,status_sekolah=status_sekolah,asal_sekolah=asal_sekolah, kegiatan_ukm=kegiatan_ukm,penghasilan_ortu=penghasilan_ortu,ips1=ips1, ips2=ips2, ips3=ips3, ips4=ips4, ips5=ips5, ips6=ips6, prediction=int(prediction))
            db.session.add(predictiondb)
            db.session.commit()
            print(nama)
            return render_template('predict.html',nama=nama, umur=umur, jenis_kelamin=jenis_kelamin,status_sekolah=status_sekolah,asal_sekolah=asal_sekolah, kegiatan_ukm=kegiatan_ukm,
            penghasilan_ortu=penghasilan_ortu,ips1=ips1, ips2=ips2, ips3=ips3, ips4=ips4, ips5=ips5, ips6=ips6, prediction=prediction)

        except ValueError:
            return "Silakan dicek kembali!"

        pass
    pass

def preprocessDataAndPredict(umur, jenis_kelamin,status_sekolah ,asal_sekolah, kegiatan_ukm, penghasilan_ortu, ips1, ips2, ips3, ips4, ips5, ips6):
    # keep all inputs in array
    test_data = [umur, jenis_kelamin, status_sekolah ,asal_sekolah, kegiatan_ukm,penghasilan_ortu, ips1, ips2, ips3, ips4, ips5, ips6]
    print(test_data)

    # convert value data into numpy array
    test_data = np.array(test_data)

    # reshape array
    test_data = test_data.reshape(1, -1)
    print(test_data)

    # open file
    file = open("wknn_model.pkl", "rb")

    # load trained model
    trained_model = joblib.load(file)

    # predict
    prediction = trained_model.predict(test_data)

    
    return prediction
    pass

@app.route('/login', methods=['GET', 'POST'])
def login():
    db.create_all()
    if request.method == 'POST':
        username = request.form.get('username') 
        password = request.form.get('password')
        if request.form['password'] == 'admin' and request.form['username'] == 'admin':
            
            session['logged_in'] = True

            return redirect('/admin')

    else:
            if session.get('logged_in'):
                return redirect('/admin')
    return render_template('login.html')
        

#menu admin
admin.add_view(UserView(Kelulusan, db.session))
admin.add_view(hasilpredik(multiPredict, db.session))
admin.add_view(Multi(name='Multi Predict', endpoint='Multi'))
admin.add_view(Rekap(name='Rekap', endpoint='Rekap'))
admin.add_view(Logout(name='Logout', endpoint='Logout'))

if __name__ == '__main__':
    app.run(debug=True)