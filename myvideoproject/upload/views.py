import os
from django.shortcuts import render, redirect
from django.conf import settings
from .forms import VideoForm
from .models import Video
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
logger = logging.getLogger(__name__)


@csrf_exempt
def upload_video(request):
    logger.debug("Request method: %s", request.method)
    logger.debug("Request POST data: %s", request.POST)
    logger.debug("Request FILES data: %s", request.FILES)

    if request.method == 'POST':
        file = request.FILES.get('file')
        if not file:
            logger.error("No file found in request.")
            return JsonResponse({'status': 'error', 'message': 'No file found'}, status=400)

        try:
            upload_id = request.POST.get('dzuuid')
            chunk_index = request.POST.get('dzchunkindex')
            total_chunks = request.POST.get('dztotalchunkcount')

            logger.debug(f"upload_id: {upload_id}, chunk_index: {chunk_index}, total_chunks: {total_chunks}")

            if not (upload_id and chunk_index is not None and total_chunks):
                logger.error("Missing upload ID, chunk index, or total chunks.")
                return JsonResponse({'status': 'error', 'message': 'Invalid request data'}, status=400)

            chunk_dir = os.path.join(settings.MEDIA_ROOT, 'chunks', upload_id)
            if not os.path.exists(chunk_dir):
                os.makedirs(chunk_dir)

            chunk_path = os.path.join(chunk_dir, f'chunk_{chunk_index}')
            with open(chunk_path, 'wb') as chunk_file:
                for chunk in file.chunks():
                    chunk_file.write(chunk)

            if int(chunk_index) + 1 == int(total_chunks):
                # Reassemble the file
                video_path = os.path.join(settings.MEDIA_ROOT, 'videos', f'{upload_id}.mp4')
                with open(video_path, 'wb') as video_file:
                    for i in range(int(total_chunks)):
                        chunk_path = os.path.join(chunk_dir, f'chunk_{i}')
                        with open(chunk_path, 'rb') as chunk_file:
                            video_file.write(chunk_file.read())

                # Clean up chunks
                for i in range(int(total_chunks)):
                    chunk_path = os.path.join(chunk_dir, f'chunk_{i}')
                    os.remove(chunk_path)
                os.rmdir(chunk_dir)

                # Save video to the database
                title = request.POST.get('title')
                content = request.POST.get('content')
                video = Video(title=title, content=content, video_file=f'videos/{upload_id}.mp4')
                video.save()
                process_video(video.video_file.path)

            return JsonResponse({'status': 'ok'})
        except Exception as e:
            logger.error(f"Error during upload: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    else:
        form = VideoForm()
    return render(request, 'upload/upload_video.html', {'form': form})

def video_list(request):
    videos = Video.objects.all().order_by('-upload_date')
    return render(request, 'upload/video_list.html', {'videos': videos})

def process_video(video_path):
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    output_dir = os.path.join(settings.MEDIA_ROOT, 'videos', base_name)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, 'index.m3u8')
    os.system(f"ffmpeg -i {video_path} -profile:v baseline -level 3.0 -s 640x360 -start_number 0 -hls_time 10 -hls_list_size 0 -f hls {output_path}")
