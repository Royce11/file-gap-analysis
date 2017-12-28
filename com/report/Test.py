import boto3

# s3 = boto3.resource('s3')
# boto3.setup_default_session()
s3 = boto3.client('s3')
keywords = {'Bucket':'idiom-vendor-data','Key':'vendor-rentrak/clean/ad-metadata/parquet/country=us/dt=2017-09-25/part-00000-2017-12-14_0116-RTDT_AdMetadata_6193_20170925.snappy.parquet'}
object = s3.head_object(**keywords)
# object = s3.head_object('idiom-vendor-data','vendor-rentrak/clean/ad-metadata/parquet/country=us/dt=2017-09-25/part-00000-2017-12-14_0116-RTDT_AdMetadata_6193_20170925.snappy.parquet')
# subresources = object.get()
print("asdasd")

# import openpyxl
# import os
#
# wb = openpyxl.Workbook()
# wb.create_sheet('sheet1',0)
# wb.create_sheet('sheet2',1)
# sheet1 = wb.get_sheet_by_name('sheet1')
# sheet2 = wb.get_sheet_by_name('sheet2')
#
# d = {'test' : [0,1,2],'foo':[342]}
# d['new', 'key'] = d.pop('test')
#
# fieldnames = ["vendor","datasource","cadence","type","country","year-month","dates","count"]
# i=1
# while i <= len(fieldnames):
#     sheet1.cell(row=1,column=i,value=fieldnames[i-1])
#     sheet2.cell(row=2,column=i,value=fieldnames[i-1])
#     i = i+1
# print (os.path.abspath('.'))
# wb.save('/home/osboxes/shared-windows10/maauun.xlsx')
# sheet1.merge_cells(start_row=2, end_row=5, start_column=1,end_column=1)
# sheet1.cell(row=2,column=1,value="Maauun")
# sheet1.append({'A':"ffsdf",'B' : "asfdsf"})
# curr = sheet1._current_row
# wb.save('/home/osboxes/shared-windows10/maauun.xlsx')
