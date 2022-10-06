# Local Imports
import os
import threading
from time import sleep

from crawler.constants import status
from crawler.constants.app_status import APP_STATUS
from crawler.constants.constant import CRAWL_SETTINGS_CONSTANTS, RAW_PATH_CONSTANTS
from crawler.constants.strings import MANAGE_CRAWLER_MESSAGES
from crawler.crawler_instance.crawl_controller.crawl_enums import CRAWL_MODEL_COMMANDS
from crawler.crawler_instance.genbot_service import genbot_controller
from crawler.crawler_instance.genbot_service.genbot_controller import genbot_instance
from crawler.crawler_instance.helper_services.helper_method import helper_method
from crawler.crawler_instance.tor_controller.tor_controller import tor_controller
from crawler.crawler_instance.tor_controller.tor_enums import TOR_COMMANDS
from crawler.crawler_services.crawler_services.mongo_manager.mongo_controller import mongo_controller
from crawler.crawler_services.crawler_services.mongo_manager.mongo_enums import MONGODB_COMMANDS, MONGO_CRUD
from crawler.crawler_shared_directory.log_manager.log_controller import log
from crawler.crawler_shared_directory.request_manager.request_handler import request_handler


class crawl_model(request_handler):

    def __init__(self):
        self.__init_image_cache()
        self.__celery_vid = 100000

    # Insert To Database - Insert URL to database after parsing them
    def __init_image_cache(self):
        if not os.path.isdir(RAW_PATH_CONSTANTS.S_CRAWLER_IMAGE_CACHE_PATH):
            os.makedirs(RAW_PATH_CONSTANTS.S_CRAWLER_IMAGE_CACHE_PATH)
        else:
            helper_method.clear_folder(RAW_PATH_CONSTANTS.S_CRAWLER_IMAGE_CACHE_PATH)

    # Start Crawler Manager
    def __install_live_url(self):
        mongo_response = mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_READ, [MONGODB_COMMANDS.S_GET_CRAWLABLE_URL_DATA, [None], [None]])
        m_live_url_list = list([x['m_url'] for x in mongo_response])
        m_request_handler, headers = tor_controller.get_instance().invoke_trigger(TOR_COMMANDS.S_CREATE_SESSION, [False])
        while True:
            try:
                m_response = m_request_handler.get(CRAWL_SETTINGS_CONSTANTS.S_START_URL, headers=headers, timeout=CRAWL_SETTINGS_CONSTANTS.S_URL_TIMEOUT, proxies={}, allow_redirects=True)
                break
            except Exception as ex:
                log.g().e(ex)
                sleep(50)

        m_response_text = m_response.text
        # m_response_text = 'http://invest2bnz2ncbp7akynqratk3aodpmfnr6noh2ipajtgtcd22acalqd.onion/\nhttp://invest2chfy3ttlf7kqv6ihr2hflzksjz2skn54etgxqlwggpmjavqid.onion/\nhttp://invest2chojkab6mnwhaeag4yy4h62tqhr4csv72cfql5qcbucshpnad.onion/\nhttp://invest2cnxirzqfzsfoqrmnpls6rbifa63yfqifur5wxgdqavpbswxqd.onion/\nhttp://invest2esyu34y64dcsuor2asc757tr26iwyvr355zsfqm2jhozy4xqd.onion/\nhttp://invest2fwzgn2um6724kbu3sq3kd3opifsmuxjumm2vgxbrlyffpbxad.onion/\nhttp://invest2gibw4fnel4ppvi3jybt2zfgllj5txzujfea3asmwwwzt4c3ad.onion/\nhttp://invest2h6rqhdpezvkl3as53d7zj26nunx7cizqej6psapkmzx4hzdyd.onion/\nhttp://invest2hqzdqet7w6remzhz3pfdudrtsp4afqp4q3oe2xpyvcbxtmqyd.onion/\nhttp://invest2j4pg52c3ba2i2s45ocpjlpoc6zeqrlv6qemta7lqxpleyp5id.onion/\nhttp://invest2l22fneg4rviqyzyyq3lf22wxva5z2k7srzrqq7odra7ons7yd.onion/\nhttp://invest2m3r2niylhghrxo3yh4jtou73sh2bdq65xfqjbbj6j3x4hb6yd.onion/\nhttp://invest2nczuxao5mfizt76minuowmkfjm2d63z6f5z77jqt4jxkyzkad.onion/\nhttp://invest2ouyltwekkmsmgqr4odkv3lbc2m7qtxkbh7rsfk42tlsiarwad.onion/\nhttp://invest2pimqzi3g4wd3s6cfjgrxq54b3enncpktlrocrf2mnakrithid.onion/\nhttp://invest2q6dfac6harktexshdawzeiqyxvodcbkxxbcjpkkt3mod7s2yd.onion/\nhttp://invest2qbmqua3fyveu3makh4hfnsxe6vm7r2x3ewwpegmhl2rhatlyd.onion/\nhttp://invest2qmlr45sk2jgiug43ifpg7ctkrt3hwvaom2saotwsnrhnupkid.onion/\nhttp://invest2rdm7yzzd4xlofk3uj4gsgxwudduvrj437xotn7lb6b453pdid.onion/\nhttp://invest2sgwxh3scyxvwqaxhlkxlcpn7ipngm5gld5pcgq72vmpezgeid.onion/\nhttp://invest2tsgv5d2vosffoaie2qxa72lz5s76af3h4zoazhre7547mzzad.onion/\nhttp://invest2ttt3bxcv5wm7pozu5ui5xaxknkxlwlvkewo3bjsntkutssrid.onion/\nhttp://invest2u3fw74sfvja5khficaetft373rzzurwdppwv73vlyz5l3e5id.onion/\nhttp://invest2vgs6d4iswmlg3dvk6eqrti2bqyrzp2dpbhuzlb2japeb7ylid.onion/\nhttp://invest2vq6uqprhj3fqwm2aox5ll75svpqo6zgmabn52vs4h2ri5guid.onion/\nhttp://invest2w37albqzruajjk446nvkehj2aswsuwkaowfp6ete3glvwy5yd.onion/\nhttp://invest2y37gxawbxnmfvodmrcg5thodajikx7g2dcfntluy73p32meid.onion/\nhttp://invest2z3szwdbdfcpvosflamvoqfgmmugpyc7hskkq57pvefgyxyoad.onion/\nhttp://invest2z744ntfsjndqlqcita65mgjzwxkwk3cdzzcof6jpl4g7kmsid.onion/\nhttp://invest3a2yonatf5fdjltgnmw7g3wxwyv3dejcafci4lxrn6u6faaoyd.onion/\nhttp://invest3cofrxpsegiylb6qm2jp7k7swylstes4hs4kw6rq7tfpbgkaqd.onion/\nhttp://invest3cuql3zwj3nk6bywfxc4zn5xa7xbijmyvxrsiaxgwfnin7vfad.onion/\nhttp://invest3do3vkvp52jvoszmj2p6gfvsmixq5d4p5mxpk3zcueoqd5adqd.onion/\nhttp://invest3eenpn5iwazjcculvzl323q62qaow3d7ijiqih7crwnidw7gqd.onion/\nhttp://invest3f2zvz5ilbpdbstoflfjeevonipdz6dn6nnioxfeebqaqdrvyd.onion/\nhttp://invest3fpn2kcqlkmyoercnf2xj2isdmgnfxbzxtr7sxcdodt6iirpid.onion/\nhttp://invest3ftejewlhrusj6b2alabxtwfiqzsovf3nzbimpn6lsrf7xv4qd.onion/\nhttp://invest3ge4gu24l2rpt5x2xu6xeupomrfskw6hl6m6dmw6irtxsgv2id.onion/\nhttp://invest3in6lgh45wsj4bogvu35mbwasjvf7lkyydmagbu55a7ghjc5ad.onion/\nhttp://invest3kz26iueustj7zgwcr6ccbpchlezm5b2ubzczkea4tlkxlpzyd.onion/\nhttp://invest3lttefuefu55dtbqz26qjom4yv6gwmu3byiayisgmygj6gklid.onion/\nhttp://invest3luvudztnqjxiqpegqhk3yokqzdejr7phk26v45bguexwbxuyd.onion/\nhttp://invest3om5gqaamtrsogwjisx2tptozgfjrztjbssk3cru7saigugmyd.onion/\nhttp://invest3pcn6z66z7qharsbcwy32dmztsixypu5pksp2y2glhyw4pi4ad.onion/\nhttp://invest3phrbggaczhejwyrneyxwgujo6u7e5w6jtcbakstmnk3ru67yd.onion/\nhttp://invest3r37psgb452da3q5rehgkvfdnndmci3w6s52jpz3en47gg5vad.onion/\nhttp://invest3rauvmrelw3esss6ad4zqaxrmkauuvlzlabexjbtrx3bz7vbqd.onion/\nhttp://invest3siptvz3p7676lfhs3o4lpbdtvgjidjgry3mdnvhgfh6qwkkad.onion/\nhttp://invest3tafvxwzhoshg7umy7gj6vjcbxukcn74p3gfkub3nusm5v53id.onion/\nhttp://invest3ttxymmh7uaci74bypzgmneykrtpwconw7czwrgsdfvxc5s3id.onion/\nhttp://invest3ul6fvtefir4mlt4ycglfmhp32ju7xywztrkfomgsxiuj4wnqd.onion/\nhttp://invest3wvhbpxff6gbe2kleinnmoor3toed64p7rdwujsojqllmvigyd.onion/\nhttp://invest3wymj4ytxupohhchqggqimtexb6zau46seapdundw2f4ialdad.onion/\nhttp://invest3y4iyeyghux5aubqevj6wqkfzwgg37aifhxx7fp7k7so4hinad.onion/\nhttp://invest3ygooc65nxkkywm3h6l5vrlrthagyiwen63gvvh6tdw2qyb4ad.onion/\nhttp://invest4aact4wdzdcvi7emgpsfp77yihith72opwaxehs7ieewss2mqd.onion/\nhttp://invest4agblzayulcwxxhtpsw35wnp7mmbm7d3yvvvxtovuawk57ycad.onion/\nhttp://invest4eyc5p5zw2pahdllaeaso3sn6vukcipsgfzhx5xlmeyhzj5iqd.onion/\nhttp://invest4fa732s7n2rr2mcn4326j3wkairncfaruklxp6bdmxgneuveqd.onion/\nhttp://invest4gihwbxz6424in46xljjcdyq37vdkdck3kiuqok6isacuax2qd.onion/\nhttp://invest4is4vgk6nplpf6qqonstvmwcdyo7z4vtx3njuvftixfogilsad.onion/\nhttp://invest4lth3r7or3buxdbasmntd7jzqbqpuz3b42ga22f3v5dd54btqd.onion/\nhttp://invest4nc6g6s27us5al7mxz7cbah7tm6u3ikixb2ooe73bbarm6g2qd.onion/\nhttp://invest4ozpuwhvz2u44zvik3acaeiazqzfhc7ebfsqn53zzujks2qdad.onion/\nhttp://invest4ppks6bizghavjsnpr5bxn4oblfzcpj3vd5npnfh2upefosaid.onion/\nhttp://invest4u6kphwajh6erk2tjiy6cac7cl4djjad3evkbk4of3j5h7vbad.onion/\nhttp://invest4xkh5ba2re3nty2osntmdzof5pdn3o7dtcsz5idqs5g5qyszyd.onion/\nhttp://invest4yd7lzevrbfx5rt7p53m3ovrmzkiq72zpc4rzshsehk6lna3qd.onion/\nhttp://invest5ad7hytwqemrxy43divirlntzqfdmko47i6rrehdehczfpggid.onion/\nhttp://invest5bkgqpqmdl5jd5qeihag2zgaosqvgrspnmy65hsh2ic6eubfyd.onion/\nhttp://invest5bzpdm4elx6mhd6hq2rvx7v6n737nqjaer54qcsg7a2guhfkyd.onion/\nhttp://invest5dju2lhdtqyqvdkln3vla673q7td6g2qinrklby6bg6zuhpfad.onion/\nhttp://invest5f4rzuh75xczgrssrznofzonosgwczcs2evjcmlyruu2zhhfid.onion/\nhttp://invest5fhdmfx6i6quradhfn6bdob3vrgwmuoqdbf7zrjv336gyy4gid.onion/\nhttp://invest5gvjmyvumauq55af2nbpr7hlitphmesxf3l4vkmi5jlb43lbqd.onion/\nhttp://invest5khy6gnzyxuxteakikjqzo6h47kkfgi4pljmh2cnkvnsgzdbid.onion/\nhttp://invest5ljolnipqvv2p47bfud6fgpwudspentrii7rwof5zqokgo2oid.onion/\nhttp://invest5owaxo62le5hgldmp7brirhq6qpaf4zmeoiez6o5jz23mcnsyd.onion/\nhttp://invest5pjrecfbwoyyhwpsxrym74nb7mravizmuc2vkkx67q7ldzgtyd.onion/\nhttp://invest5psnm2vbtgm6b7psdletrkicowfahq36lvazki722qx47l6dad.onion/\nhttp://invest5raq7oher6fvruob4kxwpebqdhij3lsz4bcyd6nmljg5bnzkyd.onion/'

        m_updated_url_list = []
        for m_server_url in m_response_text.splitlines():
            m_url = helper_method.on_clean_url(m_server_url)
            if helper_method.is_uri_validator(m_server_url) and m_url not in m_live_url_list:
                log.g().s(MANAGE_CRAWLER_MESSAGES.S_INSTALLED_URL + " : " + m_url)
                mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_UPDATE, [MONGODB_COMMANDS.S_INSTALL_CRAWLABLE_URL, [m_url], [True]])
                m_updated_url_list.append(m_url)

        mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_DELETE, [MONGODB_COMMANDS.S_REMOVE_DEAD_CRAWLABLE_URL, [list(m_live_url_list)], [None]])
        return m_live_url_list, m_updated_url_list

    def __init_docker_request(self):
        m_live_url_list, m_updated_url_list = self.__install_live_url()
        m_list = list(m_live_url_list)
        m_list.extend(m_updated_url_list)
        self.__start_docker_request(m_list)

    def __reinit_docker_request(self):
        m_live_url_list, m_updated_url_list = self.__install_live_url()
        return m_updated_url_list

    def __start_docker_request(self, p_fetched_url_list):
        virtual_id = self.__celery_vid

        while True:
            while len(p_fetched_url_list) > 0:
                if status.S_THREAD_COUNT >= CRAWL_SETTINGS_CONSTANTS.S_MAX_THREAD_COUNT:
                    sleep(5)
                    continue
                virtual_id += 1
                threading.Thread(target=genbot_instance, args=(p_fetched_url_list.pop(0), virtual_id)).start()
                status.S_THREAD_COUNT += 1

            p_fetched_url_list = self.__reinit_docker_request()
            sleep(5)

    def __start_direct_request(self):
        log.g().i(MANAGE_CRAWLER_MESSAGES.S_REINITIALIZING_CRAWLABLE_URL)

        while True:
            m_live_url_list, p_fetched_url_list = self.__install_live_url()
            m_request_list = list(m_live_url_list) + p_fetched_url_list
            for m_url_node in m_request_list:
                genbot_controller.genbot_instance(m_url_node, -1)

    def __init_crawler(self):
        self.__celery_vid = 100000
        if APP_STATUS.DOCKERIZED_RUN:
            self.__init_docker_request()
        else:
            self.__init_docker_request()

    def invoke_trigger(self, p_command, p_data=None):
        if p_command == CRAWL_MODEL_COMMANDS.S_INIT:
            self.__init_crawler()
