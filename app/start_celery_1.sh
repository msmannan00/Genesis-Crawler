celery "-A" "crawler.crawler_instance.genbot_service.genbot_controller" "purge" "-Q" "genbot_queue" "-f"
celery "-A" "crawler.crawler_instance.genbot_service.genbot_controller" "worker" "--autoscale=5,5" "--pool=gevent" "--loglevel=info" "-Q" "genbot_queue"


