from django.shortcuts import render,redirect,get_object_or_404
from .forms import UserForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from myapp03.models import Board, Comment ,Movie , Forecast  #import

from django.http.response import HttpResponse, JsonResponse
import urllib.parse
######
from myapp03 import bigdataProcess #import
from django.db.models.aggregates import Avg,Count
import os, pandas as pd



# Create your views here.

UPLOAD_DIR='../../upload'

def movie(request):
    data=[]
    bigdataProcess.movie_crawling(data)
    # data 들어있는 순서 : title, point, content
    for r in data :
        dto = Movie(title=r[0],
                    point=r[1],
                    content=r[2]) 
        dto.save()            
    return redirect('/')

def movie_chart(request):
    data=Movie.objects.values('title').annotate(point_avg = Avg('point'))[0:10]
    df = pd.DataFrame(data)
    # print(df)
    bigdataProcess.make_chart(df.title, df.point_avg)
      
    return render(request, "bigdata/chart.html",
               {"data":data, "img_data":'movie_fig.png'})

def weather(request):
    last_date = Forecast.objects.values('tmef').order_by('-tmef')[:1]
    print('last_date :' , len(last_date))
    weather = {}
    bigdataProcess.weather_crawling(last_date,weather)


    for i in weather :
        for j in weather[i] :
            dto=Forecast(city=i,tmef=j[0],wf=j[1],tmn=j[2],tmx=j[3])
            dto.save()
     

    result = Forecast.objects.filter(city='부산')
    result1 =Forecast.objects.filter(city='부산').values('wf').annotate(dcount=Count('wf')).values("dcount","wf") 
    print("result1 query :" , str(result1.query)) # sql문 보여주기

    df = pd.DataFrame(result1)
    print("df  :" , df)

    image_dic=bigdataProcess.weather_make_chart(result, df.wf, df.dcount)  
    print("image_dic  :" , image_dic) 
    return render(request,"bigdata/chart1.html",{"img_data":image_dic})               

def map(request):
    bigdataProcess.map()
    return render(request, "bigdata/map.html")    



###################

#write_form
@login_required(login_url='/login/')
def write_form(request):
    return render(request, 'board/write.html')

#list
def list(request):

    page = request.GET.get('page','1')
    word = request.GET.get('word','')
   
    boardCount = Board.objects.filter(Q(title__icontains=word)
                                |Q(content__contains=word)
                                |Q(writer__username__icontains=word)).count()
    

  
    boardList = Board.objects.filter(Q(title__contains=word)
                        |Q(content__contains=word)
                        |Q(writer__username__icontains=word)).order_by('-id')

    pageSize = 5
   
    #페이징처리
    paginator = Paginator(boardList,pageSize)  #import
    print('paginator :' , paginator)
    page_obj = paginator.get_page(page)
    print('page_obj :' , page_obj)
     
    rowNo = boardCount-(int(page)-1)*pageSize

    context ={'page_list':page_obj, 'page' : page ,
               'word':word, 'boardCount':boardCount,'rowNo':rowNo }
    return render(request, 'board/list.html',context)  

#insert
@csrf_exempt
def insert(request):
    fname=''
    fsize=0
    if 'file' in request.FILES:
        file = request.FILES['file']
        fname = file.name
        fsize = file.size
        fp = open('%s%s' %(UPLOAD_DIR, fname),'wb')
        for chunk in file.chunks():
            fp.write(chunk)
        fp.close()    

    dto = Board(writer=request.user,
            title=request.POST['title'],
            content=request.POST['content'],
            filename=fname,
            filesize=fsize
    )
    dto.save()
    return redirect("/list/")  

# download_count
def download_count(request):
    id = request.GET['id']
    dto = Board.objects.get(id =id)
    dto.down_up()
    dto.save()
    count = dto.down

    return JsonResponse({'id' : id , 'count':count})
         



            
#다운로드
def download(request):
    id = request.GET['id']
 
    dto = Board.objects.get(id =id)
    path = UPLOAD_DIR + dto.filename
    #filename = urlquote(path)  # 장고 3
    filename = urllib.parse.quote(dto.filename)  # 장고 4.0
    print("filename :", filename)
    with open(path,'rb') as file:
        response=HttpResponse(file.read(), 
                             content_type='application/octet-stream')  # import 필요함
        response['Content-Disposition']="attachment;filename*=UTF-8''{0}".format(filename)
 
        return response  

#상세보기
def detail(request, board_id):
    dto = Board.objects.get(id=board_id)
    dto.hit_up()
    dto.save()
    return render(request, 'board/detail.html',
        {'dto' : dto}) 

       

#comment_insert
@csrf_exempt
@login_required(login_url='/login/')
def comment_insert(request): 
    board_id = request.POST['id']
    board = get_object_or_404(Board, pk=board_id)   # get_object_or_404 import
    dto = Comment(
                 writer=request.user,
                 content= request.POST['content'],board=board)
    dto.save()
    #return redirect("/detail_id?id="+board_id)  
    return redirect("/detail/"+board_id)

#삭제
def delete(request, board_id):
    Board.objects.get(id=board_id).delete()
    return redirect("/list/") 

#수정 폼
def update_form(request,board_id) : 
    dto = Board.objects.get(id=board_id)
    return render(request, 'board/update.html',{'dto' : dto})           

#수정
@csrf_exempt
def update(request):
    id = request.POST['id']

    dto = Board.objects.get(id=id)
    fname = dto.filename
    fsize = dto.filesize

    if 'file' in request.FILES:
        file = request.FILES['file']
        fname = file.name
        fsize = file.size
        fp = open('%s%s' %(UPLOAD_DIR, fname),'wb')
        for chunk in file.chunks():
            fp.write(chunk)
        fp.close()  

    dto_update  = Board(id,
            writer=request.user,
            title=request.POST['title'],
            content=request.POST['content'],
            filename=fname,
            filesize=fsize)
    dto_update.save()
    return redirect('/list/')    


##################
#  sing up
def signup(request):
    if request.method == "POST":
        form = UserForm(request.POST)   #import
        if form.is_valid():
            print('signup POST is_valid')
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)  #import
            login(request,user)
            return redirect('/')
        else:
            print('signup POST un_valid')
    else:
        form = UserForm()
       
    return render(request,'common/signup.html',{'form':form})             