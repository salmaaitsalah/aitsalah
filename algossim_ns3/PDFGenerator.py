import cv2
from reportlab.platypus import SimpleDocTemplate, Image, Paragraph
from reportlab.lib.pagesizes import letter
from reportlab.platypus.tables import Table
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from datetime import datetime
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
import glob
import numpy
import pandas as pd

class PDFGenerator :
    
    def __init__(self) :
        now = datetime.now()
        dt_string = now.strftime("%d%m%Y_%H%M%S")
        self.name = f"Report_{dt_string}"
        self.doc = SimpleDocTemplate(f"report/{self.name}.pdf",
                                     pagesize=letter,
                                     rightMargin=72, leftMargin=72,
                                     topMargin=18, bottomMargin=18,
                                     title = self.name)
        self.flowables = []
        
    def GeneratePDF(self, QOS_formula, epsilon, df_acc, df_rcl, df_rcl_eval, list_df_node_info, algorithm):
        self.__AddTitle(QOS_formula, epsilon, algorithm)
        
        self.__AddSubTitle("Accuracy")
        self.__AddImage(self.__GenerateAccuracyImage())
        self.__AddTable(df_acc)
        
        self.__AddSubTitle("Recall using Label")
        self.__AddImage(self.__GenerateRecallImageLabel())
        self.__AddTable(df_rcl)
        
        self.__AddSubTitle("Confusion Matrix using Label")
        self.__AddImage(self.__GenerateConfMatrixImageLabel())
        
        self.__AddSubTitle("Recall using Evaluation")
        self.__AddImage(self.__GenerateRecallImageEval())
        self.__AddTable(df_rcl_eval)
        
        self.__AddSubTitle("Confusion Matrix using Evaluation")
        self.__AddImage(self.__GenerateConfMatrixImageEval())
        
        self.__AddSubTitle("QOS")
        self.__AddImage(self.__GenerateQOSImage())
        
        for df in list_df_node_info :
            nodeId = df.iloc[0]['nodeId']
            self.__AddSubTitle(f"Node {nodeId} Info")
            self.__AddTable(df)
        
        self.doc.build(self.flowables)

    def __concat_vh(self,list_2d): 
        return cv2.vconcat([cv2.hconcat(list_h)  for list_h in list_2d])
    
    def __hconcat_resize(self,img_list,interpolation = cv2.INTER_CUBIC):   
        h_min = min(img.shape[0] for img in img_list) 
        im_list_resize = [cv2.resize(img, (int(img.shape[1] * h_min / img.shape[0]), h_min), interpolation = interpolation)  for img in img_list] 
        
        return cv2.hconcat(im_list_resize)
    
    def __vconcat_resize(self,img_list, interpolation = cv2.INTER_CUBIC): 
        w_min = min(img.shape[1] for img in img_list) 
      
        im_list_resize = [cv2.resize(img, (w_min, int(img.shape[0] * w_min / img.shape[1])), interpolation = interpolation) for img in img_list]
        
        return cv2.vconcat(im_list_resize)

    def __GenerateAccuracyImage(self):
        imgs_path = [f for f in glob.glob("plot/*.png") if "Accuracyevolutionovertrialsnode" in f]
        #print("imgs_path : ", imgs_path)
        img_matrix = []
        img_col = []
        
        for path in imgs_path :
            #print("path : ", path)
            temp_img = cv2.imread(path)
            if (len(img_col) < 3) :
                img_col.append(temp_img)
            else :
                img_matrix.append(img_col)
                #print(img_matrix)
                img_col = []
                img_col.append(temp_img)
                
        img_matrix.append(img_col)
        
        #print("img_matrix : ", img_matrix)
        
        img_list_v = [self.__hconcat_resize(list_h, interpolation = cv2.INTER_CUBIC) for list_h in img_matrix] 
        concat_img = self.__vconcat_resize(img_list_v, interpolation=cv2.INTER_CUBIC) 
        path = "plot/AccuracyPlot.jpg"
        cv2.imwrite(path,concat_img)
        return path
    
    def __GenerateConfMatrixImageLabel(self):
        imgs_path = [f for f in glob.glob("plot/*.png") if "Confusionmatrixusinglabelnode" in f]
        
        #print("imgs_path : ", imgs_path)
        img_matrix = []
        img_col = []
        
        for path in imgs_path :
            #print("path : ", path)
            temp_img = cv2.imread(path)
            if (len(img_col) < 3) :
                img_col.append(temp_img)
            else :
                img_matrix.append(img_col)
                #print(img_matrix)
                img_col = []
                img_col.append(temp_img)
                
        img_matrix.append(img_col)
        
        #print("img_matrix : ", img_matrix)
        
        img_list_v = [self.__hconcat_resize(list_h, interpolation = cv2.INTER_CUBIC) for list_h in img_matrix] 
        concat_img = self.__vconcat_resize(img_list_v, interpolation=cv2.INTER_CUBIC) 
        path = "plot/ConfusionMatrixLabelPlot.jpg"
        cv2.imwrite(path,concat_img)
        return path
    
    def __GenerateRecallImageLabel(self):
        imgs_path = [f for f in glob.glob("plot/*.png") if "Recallevolutionovertrialsusinglabelnode" in f]
        
        #print("imgs_path : ", imgs_path)
        img_matrix = []
        img_col = []
        
        for path in imgs_path :
            #print("path : ", path)
            temp_img = cv2.imread(path)
            if (len(img_col) < 3) :
                img_col.append(temp_img)
            else :
                img_matrix.append(img_col)
                #print(img_matrix)
                img_col = []
                img_col.append(temp_img)
                
        img_matrix.append(img_col)
        
        #print("img_matrix : ", img_matrix)
        
        img_list_v = [self.__hconcat_resize(list_h, interpolation = cv2.INTER_CUBIC) for list_h in img_matrix] 
        concat_img = self.__vconcat_resize(img_list_v, interpolation=cv2.INTER_CUBIC) 
        path = "plot/RecallLabelPlot.jpg"
        cv2.imwrite(path,concat_img)
        return path
    
    def __GenerateConfMatrixImageEval(self):
        imgs_path = [f for f in glob.glob("plot/*.png") if "Confusionmatrixusingevaluationnode" in f]
        
        #print("imgs_path : ", imgs_path)
        img_matrix = []
        img_col = []
        
        for path in imgs_path :
            #print("path : ", path)
            temp_img = cv2.imread(path)
            if (len(img_col) < 3) :
                img_col.append(temp_img)
            else :
                img_matrix.append(img_col)
                #print(img_matrix)
                img_col = []
                img_col.append(temp_img)
                
        img_matrix.append(img_col)
        
        #print("img_matrix : ", img_matrix)
        
        img_list_v = [self.__hconcat_resize(list_h, interpolation = cv2.INTER_CUBIC) for list_h in img_matrix] 
        concat_img = self.__vconcat_resize(img_list_v, interpolation=cv2.INTER_CUBIC) 
        path = "plot/ConfusionMatrixEvalPlot.jpg"
        cv2.imwrite(path,concat_img)
        return path
    
    def __GenerateRecallImageEval(self):
        imgs_path = [f for f in glob.glob("plot/*.png") if "Recallevolutionovertrialsusingevaluationnode" in f]
        
        #print("imgs_path : ", imgs_path)
        img_matrix = []
        img_col = []
        
        for path in imgs_path :
            #print("path : ", path)
            temp_img = cv2.imread(path)
            if (len(img_col) < 3) :
                img_col.append(temp_img)
            else :
                img_matrix.append(img_col)
                #print(img_matrix)
                img_col = []
                img_col.append(temp_img)
                
        img_matrix.append(img_col)
        
        #print("img_matrix : ", img_matrix)
        
        img_list_v = [self.__hconcat_resize(list_h, interpolation = cv2.INTER_CUBIC) for list_h in img_matrix] 
        concat_img = self.__vconcat_resize(img_list_v, interpolation=cv2.INTER_CUBIC) 
        path = "plot/RecallEvalPlot.jpg"
        cv2.imwrite(path,concat_img)
        return path
    
    def __GenerateQOSImage(self):
        imgs_path = [f for f in glob.glob("plot/*.png") if "QOSevolutionovertrialsnode" in f]
        
        #print("imgs_path : ", imgs_path)
        img_matrix = []
        img_col = []
        
        for path in imgs_path :
            #print("path : ", path)
            temp_img = cv2.imread(path)
            if (len(img_col) < 3) :
                img_col.append(temp_img)
            else :
                img_matrix.append(img_col)
                #print(img_matrix)
                img_col = []
                img_col.append(temp_img)
                
        img_matrix.append(img_col)
        
        #print("img_matrix : ", img_matrix)
        
        img_list_v = [self.__hconcat_resize(list_h, interpolation = cv2.INTER_CUBIC) for list_h in img_matrix] 
        concat_img = self.__vconcat_resize(img_list_v, interpolation=cv2.INTER_CUBIC) 
        path = "plot/QOSPlot.jpg"
        cv2.imwrite(path,concat_img)
        return path
    
    def __GetDocWidth(self):
        return letter[0]
    
    def __GetDocHeight(self):
        return letter[1]
    
    def __AddImage(self, image_path, h_ratio=0.4):
        cv_im = cv2.imread(image_path)
        height, width, channels = cv_im.shape
        h_max = self.__GetDocHeight()*h_ratio
        w_max = self.__GetDocWidth()
        im = Image(image_path, w_max, h_max)
        self.flowables.append(im)
        
    def __AddTable(self, df_data):
        data_list = df_data.to_numpy().tolist()
        header = df_data.columns.tolist()
        data = [header] + data_list
        #print("data : ", data)
        t = Table(data, style=[('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                               ('GRID', (0,0), (-1,-1), 0.25, colors.black),
                               ('BACKGROUND', (0,0), (-1,0), colors.gray),
                               ])
        
        self.flowables.append(t)
        
    def __AddTitle(self, QOS_formula, epsilon, algorithm):
        style = getSampleStyleSheet()
        
        custom_style_header = ParagraphStyle('title1',
                                      parent = style['Heading1'],
                                      alignment = TA_CENTER)
        title = f"<u>{self.name.replace('_', ' ')}</u>"
        self.flowables.append(Paragraph(title, custom_style_header))
        
        custom_style_header_2 = ParagraphStyle('title2',
                                      parent = style['Heading2'],
                                      alignment = TA_CENTER)
        qos = f"<u>QOS formula :</u> {QOS_formula}"
        self.flowables.append(Paragraph(qos, custom_style_header_2))
        
        eps = f"<u>Epsilon :</u> {epsilon}"
        self.flowables.append(Paragraph(eps, custom_style_header_2))
        
        algo = f"<u>Algorithm choosed :</u> {algorithm}"
        self.flowables.append(Paragraph(algo, custom_style_header_2))
        
    def __AddSubTitle(self, text):
        style = getSampleStyleSheet()
        
        custom_style_header_3 = ParagraphStyle('title1',
                                      parent = style['Heading3'])
        subtitle = f"<u>{text}</u> :"
        self.flowables.append(Paragraph(subtitle, custom_style_header_3))
        