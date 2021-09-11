from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from GenesisCrawlerServices.constants.enums import CrawlerInterfaceCommands
from GenesisCrawler.controllers.serverController import ServerController


def index(request):
    return render(request, 'GenesisCrawler/index.html', )


@csrf_exempt
def command(request):
    request_command = request.POST['command']
    request_data = request.POST['json_data']


    if request_command == CrawlerInterfaceCommands.create_crawler_form_command.value:
        return render(request, 'GenesisCrawler/create_thread_blade.html', )
    else:
        return HttpResponse(ServerController.getInstance().invokeServer(request_command, request_data))

