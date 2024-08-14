import requests
import json
from bs4 import BeautifulSoup


class Rera:

    def __init__(self) -> None:
        self.projects_list = []
        self.final_response = []

    def save_as_json(self,data,file_name):
        with open(file_name, 'w') as json_file:
            json.dump(data, json_file, indent=4)

    def fetch_projects_list(self):
        url = "https://hprera.nic.in/PublicDashboard/GetFilteredProjectsPV?DistrictList%5B0%5D.Selected=false&DistrictList%5B0%5D.Value=18&DistrictList%5B1%5D.Selected=false&DistrictList%5B1%5D.Value=24&DistrictList%5B2%5D.Selected=false&DistrictList%5B2%5D.Value=20&DistrictList%5B3%5D.Selected=false&DistrictList%5B3%5D.Value=23&DistrictList%5B4%5D.Selected=false&DistrictList%5B4%5D.Value=25&DistrictList%5B5%5D.Selected=false&DistrictList%5B5%5D.Value=22&DistrictList%5B6%5D.Selected=false&DistrictList%5B6%5D.Value=26&DistrictList%5B7%5D.Selected=false&DistrictList%5B7%5D.Value=21&DistrictList%5B8%5D.Selected=false&DistrictList%5B8%5D.Value=15&DistrictList%5B9%5D.Selected=false&DistrictList%5B9%5D.Value=17&DistrictList%5B10%5D.Selected=false&DistrictList%5B10%5D.Value=16&DistrictList%5B11%5D.Selected=false&DistrictList%5B11%5D.Value=19&PlottedTypeList%5B0%5D.Selected=false&PlottedTypeList%5B0%5D.Value=P&PlottedTypeList%5B1%5D.Selected=false&PlottedTypeList%5B1%5D.Value=F&PlottedTypeList%5B2%5D.Selected=false&PlottedTypeList%5B2%5D.Value=M&ResidentialTypeList%5B0%5D.Selected=false&ResidentialTypeList%5B0%5D.Value=R&ResidentialTypeList%5B1%5D.Selected=false&ResidentialTypeList%5B1%5D.Value=C&ResidentialTypeList%5B2%5D.Selected=false&ResidentialTypeList%5B2%5D.Value=M&AreaFrom=&AreaUpto=&SearchText="
        headers = {
                    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
                    "x-requested-with":"XMLHttpRequest",
                    "host":"hprera.nic.in",
                    "referer":"https://hprera.nic.in/PublicDashboard",
                }

        response = requests.request("GET", url, headers=headers,verify=False)
        print(f"status code of fetching project list is : {response.status_code}")

        soup = BeautifulSoup(response.text,'html.parser')

        projects = soup.find_all('div', class_='shadow py-3 px-3 font-sm radius-3 mb-2')

        for project in projects:
            name = project.find('span', class_='font-lg fw-600').text.strip()
            link_tag = project.find('a', title='View Application')
            link = link_tag.text.strip()
            data_qs = link_tag['data-qs']  
            type_ = project.find_all('span')[2].text.strip()
            mobile = project.find('i', class_='fa-mobile-alt').find_next_sibling('span').text.strip()
            email = project.find('i', class_='fa-at').find_next_sibling('span').text.strip()
            address = project.find('i', class_='fa-map-marker-alt').find_next_sibling('span').text.strip()
            
            val = {
                "name":name,
                "link":link,
                "type":type_,
                "mobile":mobile,
                "email":email,
                "address":address,
                "applicationLink":data_qs
            }
            self.projects_list.append(val)

        self.save_as_json(self.projects_list,"projects_list.json")
        print("Project list are: \n")
        print(self.projects_list[:6])

    def extract_info(self,soup):
        
        data = {
            "gstinNo":None,
            "panNo":None,
            "name":None,
            "permanentAddress":None,
        }
                
        try:
            data['gstinNo'] = soup.find('td', text='GSTIN No.').find_next_sibling('td').text.strip('\nGST Certificate')
        except Exception as e:
            data['gstinNo'] = None
            
        try:
            data['panNo'] = soup.find('td', text='PAN No.').find_next_sibling('td').text.strip('\nPAN File')
        except Exception as e:
            data['panNo'] = None
        
        try:
            data['name'] = soup.find('td', text='Name').find_next_sibling('td').text.strip()
        except Exception as e:
            data['name'] = None
            
        try:
            data['permanentAddress'] = soup.find('td', text='Permanent Address').find_next_sibling('td').text.strip('\nAddress Proof')
        except Exception as e:
            data['permanentAddress'] = None

        self.final_response.append(data)

    def get_details(self):
        
        # just to find info for only 6 documents
        for data in self.projects_list[:6]:
            data_qs = data.get('applicationLink')
            url = f"https://hprera.nic.in/Project/ProjectRegistration/PromotorDetails_PreviewPV?qs={data_qs}&UpdatedChangeDets=N"
            headers = {
                    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
                    "x-requested-with":"XMLHttpRequest",
                    "host":"hprera.nic.in",
                    "referer":"https://hprera.nic.in/PublicDashboard",
                }
            res = requests.get(url,headers=headers,verify=False)
            soup = BeautifulSoup(res.text,'html.parser')
            self.extract_info(soup=soup)
        
        self.save_as_json(data=self.final_response,file_name="Final_response_only_six_data.json")


    def get_output(self):

        self.fetch_projects_list()
        self.get_details()


if __name__ == '__main__':
    Rera().get_output()
