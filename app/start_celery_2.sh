celery "-A" "crawler.crawler_instance.genbot_service.web_controller" "purge" "-Q" "web_queue" "-f"
celery "-A" "crawler.crawler_instance.genbot_service.web_controller" "worker" "--concurrency=5" "--pool=gevent" "--loglevel=info" "-Q" "web_queue"

