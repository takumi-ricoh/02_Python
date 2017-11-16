#################上NOK、下NOK#######

# -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 12:17:50 2016

@author: p000495138
"""

#インポート
import tkinter.filedialog as tkfd # ダイアログボックス
import pandas as pd #ファイルI/O
import os.path #パス設定
import numpy as np #行列計算
from scipy import interpolate
from scipy import signal
import matplotlib.pyplot as plt #グラフ

plt.close()

"""各種設定クラス"""
class Setting:
    from matplotlib.font_manager import FontProperties # 日本語を使うために必要
    fp = FontProperties(fname=r"C:\Windows\Fonts/HGRSMP.ttf") # フォントファイルの場所を指定

"""データファイル読み出しクラス"""
class ReadDataFile:
    
    #コンストラクタ
    def __init__(self):
        self.pickdata()
        self.readfile()
        self.size1,self.size2 =self.exp_data1.shape
        self.namedata()
        
    #ファイル選択
    def pickdata(self):
        fTyp=[('ファイル','*.csv')];
        iDir='K:\06 SEMITEC'; #初期ディレクトリ
        filename_full=tkfd.askopenfilename(filetypes=fTyp,initialdir=iDir)#フォルダ含む
        self.filename=os.path.basename(filename_full) #ファイル名のみ抽出

    #ファイル読み出し(pandas → numpy)
    def readfile(self):
        col_names = [ 'c{0:02d}'.format(i) for i in range(20) ]#そのままだとエラーになるので列数指定
        data0_pd = pd.read_csv(self.filename,encoding = "ISO-8859-1",names=col_names);#エンコード指定
        [size01,size02] = data0_pd.shape #データサイズ取得
        data1_pd=data0_pd.ix[63:(size01-4),'c02':'c17']#数値部分の切り出し
        self.exp_data1 = data1_pd.as_matrix().astype(float) #arra
        
    #データの割り振り
    def namedata(self):
        self.t=np.linspace(0.0,self.size1*0.1,self.size1)
        self.Vcomp            = self.exp_data1[:,0]; #ニップ前
        self.Vcc              = self.exp_data1[:,1]; #ニップ前
        self.Vdet             = self.exp_data1[:,2]; #ニップ前
        self.Tempature        = self.exp_data1[:,3]; #ニップ前

"""テーブル読み出しクラス"""
class ReadNCTable:    
    
    #コンストラクタ
    def __init__(self):
        self.filename = 'K:/06 SEMITEC/SEMITEC_NCtable.csv'
        self.readtable()
        self.namedata()
        
    #テーブル読み込み
    def readtable(self):
        filename=self.filename
        self.raw = np.loadtxt(self.filename,delimiter=",")       
        
    #データの割り振り
    def namedata(self):
        self.Vcomp_table            = self.raw[1:,1 ]; #ニップ前\
        self.Tcomp_table            = self.raw[1:,0 ]; #ニップ前
        self.Vdet_table             = self.raw[1:,2:]; #ニップ前\
        self.Tdet_table             = self.raw[0 ,2:]; #ニップ前\        

"""温度計算クラス"""
class Tcalc:
    
    #コンストラクタ
    def __init__(self,Vdet,Vcomp,Vdet_table,Vcomp_table,Tdet_table,Tcomp_table):
        #変数セット
        self.Vdet   = Vdet
        self.Vcomp  = Vcomp
        self.Vdet_table = Vdet_table
        self.Vcomp_table = Vcomp_table
        self.Tdet_table = Tdet_table
        self.Tcomp_table = Tcomp_table    
        #サイズセット
        self.set_size()
        #温度計算
        self.calc_tdet()
        self.calc_tcomp()
 
    #サイズなどのセット   
    def set_size(self):
        self.Table_col,self.Table_row = np.shape(self.Vdet_table)
        self.expsize = len(self.Vdet)          

    #検知温度計算
    def calc_tdet(self):
        
        #step1 補償 → 検知のマッピング
        fc=[]
        for i in range(self.Table_row):
            temp = interpolate.interp1d(self.Vcomp_table,self.Vdet_table[:,i],bounds_error=False,fill_value=3)
            fc.append(temp)
    
        #step2～step4 計測データ毎に温度換算
        self.Tdet=[]
    
        for k in range(self.expsize):
            #step2 検知出力候補を、補償を内挿して出す。
            fd=[]
            for i in range(self.Table_row): #1列ずつ
                temp  = fc[i](self.Vcomp[k])
                fd.append(temp) 
            
            #step3 検知→温度 のマッピング
            ft = interpolate.interp1d(fd,self.Tdet_table,bounds_error=False,fill_value=3) #
                        
            #step4 検知温度の計算
            self.Tdet.append( ft(self.Vdet[k]) )
        
    #補償温度計算
    def calc_tcomp(self):
        #step1 補償→補償温度のマッピング
        f = interpolate.interp1d(self.Vcomp_table,self.Tcomp_table,bounds_error=False,fill_value=3)
        
        #step2 温度計算
        self.Tcomp = f(self.Vcomp)

"""プロットクラス"""
class MyPlot:
    #コンストラクタ
    def __init__(self,data,Ttrue,calc):
        self.t      = data.t
        self.Ttrue  = Ttrue
        self.Tdet   = calc.Tdet
        self.Tcomp  = calc.Tcomp

    #プロット
    def myplot(self):
        
        self.fig1 = plt.figure() #インスタンス生成
        self.ax1 = self.fig1.add_subplot(211) 
        self.ax2 = self.fig1.add_subplot(212)  
        
        #プロット1
        self.ax1.plot(self.t,self.Ttrue)
        self.ax1.plot(self.t,self.Tdet)
        self.ax1.plot(self.t,self.Tcomp)
        self.setplot(self.ax1,'sec','deg',0,1000,20,200,['Ttrue','Tdet','Tcomp'])

        #プロット2
        self.ax2.plot(self.t,self.Tdet - self.Ttrue)    
        self.setplot(self.ax2,'sec','error',0,1000,-50,50,['Error'])
        
    #プロットの設定
    def setplot(self,ax,xlab,ylab,xmin,xmax,ymin,ymax,legend):
        ax.grid(True)
        ax.set_xlabel(xlab)
        ax.set_ylabel(ylab)        
        ax.set_xlim(xmin,xmax)
        ax.set_ylim(ymin,ymax)
        ax.legend(legend)

"""  実行部分（計算）  """
Setting() #初期セッティング
table1  = ReadNCTable() #テーブル読み込み実行
data1   = ReadDataFile() #データ読み込み実行


#インスタンス生成
calc1  = Tcalc(data1.Vdet, data1.Vcomp, table1.Vdet_table, table1.Vcomp_table, table1.Tdet_table, table1.Tcomp_table) 
Tdet1  = np.array(calc1.Tdet) #値読み出し
Tcomp1 = np.array(calc1.Tcomp) #値読み出し

"""  実行部分(プロット)  """

plot1 = MyPlot(data1,data1.Tempature,calc1) #インスタンス生成
plot1.myplot() #値セット

"""  結果保存  """
res=np.array([data1.t, data1.Tempature, calc1.Tdet, calc1.Tcomp])
res=res.T
res_pd = pd.DataFrame(res) #データフレーム化
res_pd.columns= ['t','Ttrue','Tdet','Tcomp']; #データフレームの列に名前をつける
res_name = data1.filename + "_res.CSV" #保存名
res_pd.to_csv(res_name); #ｃｓｖ保存
