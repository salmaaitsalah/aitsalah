
## @file PDFGenerator.py
#  @brief File where everything related to the pdf generation is defined
#  @details In this file, we define PDFGenerator, the class that allows us to generate a PDF Report of the simulation.
#   We also define PDFGeneratorVar, a struct class that regroup all variable needed to generate the PDF Report.
# @author: Romain Durieux and Nathan Trouillet (2022)

import cv2
from reportlab.platypus import SimpleDocTemplate, Image, Paragraph
from reportlab.lib.pagesizes import letter
from reportlab.platypus.tables import Table
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
import os
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
import glob
import numpy
import pandas as pd

## @brief Initialization of PDFGeneratorVar class.
# @details
# @param Namespace args: the argsParser object from the main
class PDFGeneratorVar :
    def __init__(self, args):
        
        self.list_node_id = []
        self.list_L = []
        self.list_C = []
        self.list_eps = []
        self.list_rcl = []
        self.list_pre = []
        self.list_spe = []
        self.list_acc = []
        self.list_perf = []
         
        self.dict_acc = {}
        self.dict_rcl = {}
        self.dict_rcl_eval = {}
        
        self.title_report = args.title_report
        self.C = args.C
        self.L = args.L
        self.epsilon = args.epsilon
        self.algo = args.name_algo
        self.qos_mode = args.mode
        self.nb_node = args.nb_node


class PDFGenerator :
## @brief Initialization of the PDFGenerator class.
# @details 
# @param string name: name of the report
    def __init__(self, name) :
     
        self.name = name
        #initialization of a simple doc template
        self.doc = SimpleDocTemplate(f"report/{self.name}.pdf",
                                     pagesize=letter,
                                     rightMargin=72, leftMargin=72,
                                     topMargin=18, bottomMargin=18,
                                     title = self.name)
        #initialization of the flowables, a list which will contains all the PDF element that will compose the PDF Report
        self.flowables = []
        
## @brief Method that add all the element in the flowables list (using privates methods) and then build the PDF File using all the elements in the flowables list
# @details 
# @param PDFGeneratorVar generator_var: Object containing all the needed variable for the PDF Generation
# @param DataFrame df_acc: Dataframe of the final accuracy for each node
# @param DataFrame df_rcl : Dataframe of the final recal value using the label for each node
# @param DataFrame df_rcl_eval : Dataframe of the final recal value using the evaluation for each node
# @param list list_df_node_info: List containing all the data from each node in a dataframe (one per node)
# @param DataFrame df_value: Dataframe of the values relatives to the resumed performance of each nodes
# @param float global_performance: Global performance value (between 0 and 1)

    def GeneratePDF(self, generator_var, df_acc, df_rcl, df_rcl_eval, list_df_node_info, df_value, global_performance):
     
        C = generator_var.C
        L = generator_var.L 
        epsilon = generator_var.epsilon
        algorithm = generator_var.algo
        mode = generator_var.qos_mode
        QOS_formula = generator_var.title_report
        if not os.path.exists(f"report/{self.name}.pdf") :
            self.__AddTitle(QOS_formula, epsilon, algorithm, C, L, global_performance, mode)
            
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
            
            self.__AddSubTitle("Resumed Performance of all nodes")
            self.__AddTable(df_value)
            
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

## @brief Method that concatenates all the saved accuracy plot in one image
# @details 
#@return    path    path of the saved image
    def __GenerateAccuracyImage(self):

        imgs_path = [f for f in glob.glob("plot/*.png") if "Accuracyevolutionovertrialsnode" in f]
        img_matrix = []
        img_col = []
        
        for path in imgs_path :

            temp_img = cv2.imread(path)
            if (len(img_col) < 3) :
                img_col.append(temp_img)
            else :
                img_matrix.append(img_col)

                img_col = []
                img_col.append(temp_img)
                
        img_matrix.append(img_col)
        
        
        img_list_v = [self.__hconcat_resize(list_h, interpolation = cv2.INTER_CUBIC) for list_h in img_matrix] 
        concat_img = self.__vconcat_resize(img_list_v, interpolation=cv2.INTER_CUBIC) 
        path = "plot/AccuracyPlot.jpg"
        cv2.imwrite(path,concat_img)
        return path
## @brief Method that concatenates all the saved Confusion Matrix using the label plot in one image
# @details 
# @return   path  path of the saved image

    def __GenerateConfMatrixImageLabel(self):
        
        imgs_path = [f for f in glob.glob("plot/*.png") if "Confusionmatrixusinglabelnode" in f]
        
        img_matrix = []
        img_col = []
        
        for path in imgs_path :
            temp_img = cv2.imread(path)
            if (len(img_col) < 3) :
                img_col.append(temp_img)
            else :
                img_matrix.append(img_col)
                img_col = []
                img_col.append(temp_img)
                
        img_matrix.append(img_col)
        
        
        img_list_v = [self.__hconcat_resize(list_h, interpolation = cv2.INTER_CUBIC) for list_h in img_matrix] 
        concat_img = self.__vconcat_resize(img_list_v, interpolation=cv2.INTER_CUBIC) 
        path = "plot/ConfusionMatrixLabelPlot.jpg"
        cv2.imwrite(path,concat_img)
        return path
## @brief Method that concatenates all the saved Recall using the label plot in one image
# @details 
# @return   path  path of the saved image
    def __GenerateRecallImageLabel(self):
        imgs_path = [f for f in glob.glob("plot/*.png") if "Recallevolutionovertrialsusinglabelnode" in f]
        
        img_matrix = []
        img_col = []
        
        for path in imgs_path :
            temp_img = cv2.imread(path)
            if (len(img_col) < 3) :
                img_col.append(temp_img)
            else :
                img_matrix.append(img_col)
                img_col = []
                img_col.append(temp_img)
                
        img_matrix.append(img_col)
        
        
        img_list_v = [self.__hconcat_resize(list_h, interpolation = cv2.INTER_CUBIC) for list_h in img_matrix] 
        concat_img = self.__vconcat_resize(img_list_v, interpolation=cv2.INTER_CUBIC) 
        path = "plot/RecallLabelPlot.jpg"
        cv2.imwrite(path,concat_img)
        return path
## @brief Method that concatenates all the saved Confusion matrix using the evaluation plot in one image
# @details 
# @return   path  path of the saved image  
    def __GenerateConfMatrixImageEval(self):
        imgs_path = [f for f in glob.glob("plot/*.png") if "Confusionmatrixusingevaluationnode" in f]
        
        img_matrix = []
        img_col = []
        
        for path in imgs_path :
            temp_img = cv2.imread(path)
            if (len(img_col) < 3) :
                img_col.append(temp_img)
            else :
                img_matrix.append(img_col)
                img_col = []
                img_col.append(temp_img)
                
        img_matrix.append(img_col)
        
        
        img_list_v = [self.__hconcat_resize(list_h, interpolation = cv2.INTER_CUBIC) for list_h in img_matrix] 
        concat_img = self.__vconcat_resize(img_list_v, interpolation=cv2.INTER_CUBIC) 
        path = "plot/ConfusionMatrixEvalPlot.jpg"
        cv2.imwrite(path,concat_img)
        return path
## @brief Method that concatenates all the saved Recall using the evaluation  plot in one image
# @details 
# @return   path  path of the saved image   
    def __GenerateRecallImageEval(self):
        imgs_path = [f for f in glob.glob("plot/*.png") if "Recallevolutionovertrialsusingevaluationnode" in f]
        
        img_matrix = []
        img_col = []
        
        for path in imgs_path :
            temp_img = cv2.imread(path)
            if (len(img_col) < 3) :
                img_col.append(temp_img)
            else :
                img_matrix.append(img_col)
                img_col = []
                img_col.append(temp_img)
                
        img_matrix.append(img_col)
        
        
        img_list_v = [self.__hconcat_resize(list_h, interpolation = cv2.INTER_CUBIC) for list_h in img_matrix] 
        concat_img = self.__vconcat_resize(img_list_v, interpolation=cv2.INTER_CUBIC) 
        path = "plot/RecallEvalPlot.jpg"
        cv2.imwrite(path,concat_img)
        return path
## @brief Method that concatenates all the saved QOS evolution plot in one image
# @details 
# @return   path  path of the saved image 
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
## @brief Method that add an image to the flowables list 
# @details 
#@param string image_path: path of the image
#@param float h_ratio: height ratio of the image (compared to the page). Default = 0.4

    def __AddImage(self, image_path, h_ratio=0.4):
        
        cv_im = cv2.imread(image_path)
        height, width, channels = cv_im.shape
        h_max = self.__GetDocHeight()*h_ratio
        w_max = self.__GetDocWidth()
        im = Image(image_path, w_max, h_max)
        self.flowables.append(im)
## @brief Method that add a table to the flowables list depending of the input dataframe
# @details 
#@param DataFrame df_data: dataframe containing the wanted data  
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
## @brief Method that add the main title to the flowables list
# @details 
#@param string QOS_formula: Title of the report
#@param float epsilon: epsilon value
#@param string algorithm: name of the selected algotithm
#@param float C: C value
#@param float L: L value
#@param float global_performance: global performance value
#@param string mode : QOS computation mode selected   
    def __AddTitle(self, QOS_formula, epsilon, algorithm, C, L, global_performance, mode):
        
        style = getSampleStyleSheet()
        
        custom_style_header = ParagraphStyle('title1',
                                      parent = style['Heading1'],
                                      alignment = TA_CENTER)
        title = f"<u>{self.name.replace('_', ' ')}</u>"
        self.flowables.append(Paragraph(title, custom_style_header))
        
        custom_style_header_2 = ParagraphStyle('title2',
                                      parent = style['Heading2'],
                                      alignment = TA_CENTER)
        qos = f"{QOS_formula}"
        self.flowables.append(Paragraph(qos, custom_style_header_2))
        
        eps = f"<u>Epsilon :</u> {epsilon}"
        self.flowables.append(Paragraph(eps, custom_style_header_2))
        
        algo = f"<u>Algorithm choosed :</u> {algorithm}"
        self.flowables.append(Paragraph(algo, custom_style_header_2))
        
        C_L_value = f"<u>C :</u> {C} \t <u>L : </u> {L}"
        self.flowables.append(Paragraph(C_L_value, custom_style_header_2))
        
        perf = f"<u>Mode : </u> {mode} <u>Global performance : </u> {global_performance}"
        self.flowables.append(Paragraph(perf, custom_style_header_2))
##@brief Method that add a subtitle to the flowables list
# @details      
# @param string text: Text of the title
    def __AddSubTitle(self, text):
        
        style = getSampleStyleSheet()
        
        custom_style_header_3 = ParagraphStyle('title1',
                                      parent = style['Heading3'])
        subtitle = f"<u>{text}</u> :"
        self.flowables.append(Paragraph(subtitle, custom_style_header_3))

## @brief public method that allows us to generate the PDF
# @details  
#@param PDFGeneratorVar generator_var: Object containing all the needed variable for the PDF Generation
#@param dict dict_value: Dictionnary of the values relatives to the resumed performance of each nodes
#@param float global_performance: global performance value
#@param string mode : QOS computation mode selecteds      
def generatePDF(generator_var, dict_value, global_performance,name):
  

    print(f"==================================================> {name}.pdf")

    df_acc = pd.DataFrame(generator_var.dict_acc, index=[0]).iloc[:, ::-1]
    df_acc[' '] = ['Accuracy']
    df_acc = df_acc.iloc[:, ::-1]

    df_rcl = pd.DataFrame(generator_var.dict_rcl, index=[0]).iloc[:, ::-1]
    df_rcl[' '] = ['Recall']
    df_rcl = df_rcl.iloc[:, ::-1]

    df_rcl_eval = pd.DataFrame(generator_var.dict_rcl_eval, index=[0]).iloc[:, ::-1]
    df_rcl_eval[' '] = ['Recall using evaluation']
    df_rcl_eval = df_rcl_eval.iloc[:, ::-1]
    
    df_value = pd.DataFrame(dict_value)

    print("Finding data files")
    list_df_node_info = []
    list_dir = [f for f in glob.glob("./data/*") if "node" in f]
    for d in range(0, generator_var.nb_node):
        list_df_node_info.append(pd.read_csv(f'{list_dir[d]}/data.txt'))

    generator = PDFGenerator(name=name)
    print(f"Generating PDF : {name}")
    generator.GeneratePDF(generator_var,
                          df_acc=df_acc, df_rcl=df_rcl, df_rcl_eval=df_rcl_eval,
                          list_df_node_info=list_df_node_info,
                          df_value = df_value, global_performance = global_performance)
