import re
import xlsxwriter 
workbook = xlsxwriter.Workbook('Delhi.xlsx') 
worksheet = workbook.add_worksheet() 
from robobrowser import RoboBrowser
from bs4 import BeautifulSoup

a=[]
b=[]
date1=[]
row = 1
stop = 0

worksheet.write(0, 0, "Patient Name")
worksheet.write(0, 1, "Patient ID")
worksheet.write(0, 2, "Parent Link")
worksheet.write(0, 3, "Phone Number")
worksheet.write(0, 4, "Admission Date")
worksheet.write(0, 5, "Observation")

br=RoboBrowser()
br.open("https://cloud.pappyjoe.com")
form=br.get_form()
form['username']=' '
form['password']=' '
br.submit_form(form)
next_page='https://cloud.pappyjoe.com/clinic/patients'

for i in range(2,100):
    br.open(str(next_page))
    src=str(br.parsed())
    soup = BeautifulSoup(src, features = 'lxml')
    soup=soup.find("div", {"class": "my-form"})
    next_page=soup.find("ul", {"class": "pagination"})
    try:
        next_page=re.search('"https://cloud.pappyjoe.com/clinic/patients/'+'[0-9]+'+'">'+str(i),str(next_page)).group(0)
        next_page=re.sub('"','',str(next_page))
        next_page=re.sub('>'+str(i),'',str(next_page))
        print(next_page)
    except(AttributeError):
        stop=1

    soup=soup.find("div", {"class": "col-lg-12 col-md-12 col-sm-12 col-xs-12 padding0"})
    a_1='https://cloud.pappyjoe.com/clinic/view_patient/'
    a_2='">'
    a=re.findall(str(a_1)+'[1023456789]*',str(soup))

    def extract(name,soup,date,row,column):
        a=[]
        b=[]
        c=[]
        soup1=soup.find("div", {"id": str(name)})
        soup1=soup1.findAll("div", {"class": 'col-lg-3 col-md-3 col-sm-3 col-xs-3 padding0'})
        [a.append(i.text.strip()) for i in soup1]
        soup2=soup.find("div", {"id": str(name)})
        soup2=soup2.findAll("div", {"class": 'col-lg-12 col-md-12 col-sm-12 col-xs-12'})
        [b.append(i.text.strip()) for i in soup2]
        c.append(date)
        [c.append(str(a[i])+":"+str(b[i])) for i in range(len(a))]
        soup3=soup.find("div", {"id": str(name)})
        soup3=soup3.find("div", {"class": 'col-lg-12 col-md-12 col-sm-12 col-xs-12 grey fontstyle'})
        soup3=soup3.text.strip()
        d=re.split(':',soup3)[1]
        c.append('Treated By:'+str(d[1:]))
        worksheet.write(row, column,'\n'.join(c))
        if  column==6:
            for index, i in enumerate(c): 
                if 'Observations:' in str(i):
                    j=re.search('[0-9]+%',str(i))
                    if j:
                        j=j.group()
                        j=re.search('[0-9]+',j).group()
                        j='Observations:'+str(j)+'%'
                        j=j+'\n'+str(re.sub('Observations:','',str(c[index])))
                    else:
                        j=str(c[index])
                    worksheet.write(row,5,j)
                
    
    for i in a:
        date1=[]
        print(i)
        br.open(i)
        #......Phone Number......
        
        src=str(br.parsed())
        src1=src
        soup = BeautifulSoup(src, 'html.parser')
        soup=soup.find("div", {"class": "col-lg-8 col-md-8 col-sm-8 col-xs-8 border-right"})
        text = soup.get_text()
        admission_date = text.split()
        for index,i_1 in enumerate(admission_date):
            if 'Admission' == str(i_1):
                #print(admission_date[index+2])
                if admission_date[index+2] !='Contact':
                    worksheet.write(row, 4, admission_date[index+2])
        
        if re.search('\+[0-9]+', text):
            code=re.search('\+[0-9]+', text).group()
        if re.search('[0-9]{6,}', text):
            phone_number=re.search('[0-9]{6,}', text).group()
        if phone_number:
            if code:
                phone_number=code+' '+phone_number
                b.append(phone_number)
         
    
        #........................
        br.open('https://cloud.pappyjoe.com/clinic/clinic_notes')
        src=str(br.parsed())
        soup = BeautifulSoup(src, 'html.parser')
        patient_id=soup
        soup=soup.find("div", {"style": "margin-top:80px;"})
        #print(soup)
        soup=soup.find("div", {"class": "col-lg-10 col-md-8 col-sm-12 col-xs-12 white"})
        #print(soup)
        date=soup.findAll("h4")
        [date1.append(i.text.strip()) for i in date]
                    
# name of patients....................
        if re.search('<strong>Patient Name:</strong>\ '+'[A-Za-z ]*'+'</label>', str(soup)):        
            name=re.search('<strong>Patient Name:</strong>\ '+'[A-Za-z ]*'+'</label>', str(soup)).group(0)
            name=re.sub('<strong>Patient Name:</strong>\ ','', name)
            name=re.sub('</label>','', name)
            #print(name)
            column=0
            
            worksheet.write(row, column, name.strip())
# patients_id....................
            if re.search('Patient ID : '+'[A-Za-z ]*', str(patient_id)):        
                name_id=re.search('Patient ID :'+'[A-Za-z0-9 ]*', str(patient_id)).group(0)
                name_id=re.sub('Patient ID :','', name_id)
                name_id=name_id.strip()
                worksheet.write(row, 1, name_id)
                if phone_number:
                    #print(phone_number)
                    worksheet.write(row, 3,phone_number)
                worksheet.write_url(row, 2, str(i))

# Date....................
            list_1=(str(soup).split('\n'))
            i=0
            column=6
            for index,data in enumerate(list_1):
                if '<h4>' in data:
                    list_1_id=list_1[index+2]
                    name=re.search('id="'+'[A-Za-z0-9_]*'+'"', list_1_id)
                    name=re.sub('id="','',str(name.group()))
                    name=re.sub('"','', str(name))
                    date=date1[i]
                    extract(name,soup,date,row,column)
                    i+=1
                    column+=1
        else:
            soup = BeautifulSoup(src1, 'html.parser')
            soup=soup.find("p", {"class": "text-box"})
            soup=soup.find("label", {"class": "col-lg-4 col-md-4 col-sm-12 col-xs-12 control-label text-left"})
            name=soup.get_text().strip()
            #print(name)
            worksheet.write(row, 0, name.strip())
        row += 1
    if stop==1:
        workbook.close()
        break
    
workbook.close()

