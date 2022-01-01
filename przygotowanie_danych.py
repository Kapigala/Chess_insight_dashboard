import pandas as pd
import csv

f_g={14204118:'Abdusattorov (17)',12573981:'Firouzja (18)',1503014:'Carlsen (31)',1170546:'Duda (23)',2016192:'Nakamura (34)',4147103:'Goryachkina (23)',5000017:'Anand (52)'}
file_path='C:\\Users\\Kacper\\Desktop\\Baza Danych szachy\\players.csv'
gracze=pd.read_csv(file_path)
gracze=gracze[gracze['title'].isnull()==False]
h=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec','fide_id']

a_2015=pd.read_csv('ratings_2015.csv')
a_2016=pd.read_csv('ratings_2016.csv')
a_2017=pd.read_csv('ratings_2017.csv')
a_2018=pd.read_csv('ratings_2018.csv')
a_2019=pd.read_csv('ratings_2019.csv')
a_2020=pd.read_csv('ratings_2020.csv')

for tempo in ['rating_standard','rating_rapid','rating_blitz']:
    for i in [a_2015,a_2016,a_2017,a_2018,a_2019,a_2020]:
        f = open('chess_{}_{}.csv'.format(i['year'][0],tempo), 'w')
        writer = csv.writer(f)
        for k in pd.unique(gracze['fide_id']):
            row=i.loc[i['fide_id']==k][tempo].values.tolist()
            row.append(k)
            writer.writerow(row)

ff = open('comparision.csv','w')
writer = csv.writer(ff)

for k in ['standard','rapid','blitz']:
    p=[14204118,12573981,1503014,1170546,2016192,4147103,5000017]
    for n in range(len(p)):
        zawodnik=[k,p[n]]
        for i in ['2015','2016','2017','2018','2019','2020']:
            dane=pd.read_csv('chess_{}_rating_{}.csv'.format(i,k),names=h)
            z=dane[dane['fide_id']==p[n]][['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']].values.tolist()
            zawodnik.extend(z[0])
        writer.writerow(zawodnik)

fg = open('szereg.csv','w')
writer = csv.writer(fg)
fid=[14204118,12573981,1503014,1170546,2016192,4147103,5000017]
ll=[]
for k in ['standard','rapid','blitz']:
    for s in ['2015','2016','2017','2018','2019','2020']:
        for ss in range(1,13):
            d=pd.read_csv('chess_{}_rating_{}.csv'.format(s,k),names=h)
            for p in fid:
                x=d[d['fide_id']==p].values.tolist()
                writer.writerow([k,'{}-{}'.format(s,ss),f_g[p],x[0][ss-1]])


