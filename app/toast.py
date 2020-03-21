import requests
from django.http import HttpResponse, Http404


def get_token():
    auth_url = 'https://api-compute.cloud.toast.com/identity/v2.0'
    tenant_id = '2426bc68736b4ca186199174c5d570bc'
    username = 'gwngus3922@gmail.com'
    password = 'qpsej0424'
    token_url = auth_url + '/tokens'
    req_header = {'Content-Type': 'application/json'}
    req_body = {
        'auth': {
            'tenantId': tenant_id,
            'passwordCredentials': {
                'username': username,
                'password': password
            }
        }
    }

    response = requests.post(token_url, headers=req_header, json=req_body)
    return response.json()


class ContainerService:
    account = 'AUTH_2426bc68736b4ca186199174c5d570bc'
    url = ''
    token_id = ''

    def __init__(self, url, token_id):
        self.url = url
        self.token_id = token_id

    def _get_url(self, container):
        return self.url + self.account + '/' + container

    def _get_list(self, req_url):
        req_header = {'X-Auth-Token': self.token_id}
        response = requests.get(req_url, headers=req_header)
        return response.content.decode().split('\n')

    def get_object_list(self, container):
        req_url = self._get_url(container)
        return self._get_list(req_url)

    def _get_request_header(self):
        return {'X-Auth-Token': self.token_id}

    def create(self, container):
        req_url = self._get_url(container)
        req_header = self._get_request_header()
        return requests.put(req_url, headers=req_header)

    def set_read_acl(self, container, is_public):
        req_url = self._get_url(container)
        req_header = self._get_request_header()
        req_header['X-Container-Read'] = '.r:*' if is_public else ''
        return requests.post(req_url, headers=req_header)


class ObjectService:
    account = 'AUTH_2426bc68736b4ca186199174c5d570bc'
    url = ''
    token_id = ''
    dir_path = ''

    def __init__(self, url, token_id):
        self.url = url
        self.token_id = token_id

    def _get_url(self, container, object_name):
        return self.url + self.account + '/' + container + '/' + object_name

    def _get_request_header(self):
        return {'X-Auth-Token': self.token_id}

    def upload(self, container, object, file):
        req_url = self._get_url(container, object)
        req_header = self._get_request_header()

        requests.put(req_url, headers=req_header, data=file)

    def delete(self, container, object):
        req_url = self._get_url(container, object)
        req_header = self._get_request_header()
        requests.delete(req_url, headers=req_header)

    def download(self, container, object_name):
        req_url = self._get_url(container, object)
        req_header = self._get_request_header()
        # print(req_url)
        response = requests.get(req_url, headers=req_header)

        if response.status_code == 200:
            deliver_response = HttpResponse(content_type='video/mp4')
            # force browser to download file
            deliver_response['Content-Disposition'] = 'attachment; filename=%s' % object_name
            deliver_response.write(response.content)
        else:
            raise Http404

        return deliver_response

    def get_image_and_video_files_download_url(self, id, vm_no, object_list):
        url_list = []
        idx = 0
        idx2 = 0
        idx3 = 0
        idx4 = 0
        for object in object_list:
            if vm_no in object and "ProductImages" in object and "." in object:
                tmp_json = {"ProductImages%d" % idx: self._get_url(id, object)}
                url_list.append(tmp_json)
                idx += 1
            elif vm_no in object and "ProductDetailImages" in object and "." in object:
                tmp_json = {"ProductDetailImages%d" % idx2: self._get_url(id, object)}
                url_list.append(tmp_json)
                idx2 += 1
            elif vm_no in object and "PromotionVideos" in object and "." in object:
                tmp_json = {"PromotionVideos%d" % idx3: self._get_url(id, object)}
                url_list.append(tmp_json)
                idx3 += 1
            elif vm_no in object and "VideosThumbnail" in object and "." in object:
                tmp_json = {"VideosThumbnail%d" % idx3: self._get_url(id, object)}
                url_list.append(tmp_json)
                idx4 += 1

        return url_list