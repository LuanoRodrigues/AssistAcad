from Zotero_module.zotero_class import  Zotero
import os
from dotenv import load_dotenv
load_dotenv()  # loads the variables from .env
import os



# # Set environment variables explicitly
# os.environ["LIBRARY_ID"] = "9047943"
# os.environ["API_KEY"] = "24POAbOlMnLkqFUoBCk3g5t6"
# os.environ["LIBRARY_TYPE"] = "user"
# os.environ["TOKEN"] = "eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..2SODEe_PcYJmXZ5i.FFrSfX7I9fBTtGrDQyAN7GtaLYVWtsZpOnoBDQ24GSnEzkkKT4eZZKMOh-RKlgl0NV7j-WQFQACfu7JACjgej9b6NYTPtSuZnqxSoL-JQ5PWq6ExnjTvGSFmR91EApQlDTFDl2431Mrtbb22yNAGuEg6JqLBCSmhv_2JpIIjflZ1rHEVjxjjbZDmsr4ZNRFnzVmz6hmviw-sLJg6O0tctHCkh-qcLLxdRElbSrYfLXhsp8DezN_dMLIqRIVcpfm4k-yxGLGSs-TIGDbIfOtKZgdrBSD-6Q2RdyamdcIhKnjtqBhleyafCgwgK9_QoZYdDO3qmb1_AMTG92m8PPo1C_uNAV8YEt-iNNlm2WxgEaLr2-IrmXUnugII5_fNAblnF4fg5lR2bKZGqBHThAI5ZLQK_YyGA5t-g8mAQBw9EODCCQfwUOFPproGniw5aDDduUd5sUA_IxZTXXDpr6PAWULmijZ9sU7Vk1TXIpLVWrYHKq1xsUrb2gKntjhSwELiMApj_1_7DmN3HRphp3heBqyQCVDrO4QVbSVYh8ZsLR2WTTnSsFfYxNQvpVis8UTC98MGZD26jsPpDPJ5tWpKgFdnc5hyOxO1CIjf_irMw6CyZWZYQst2cEC3QUx6zaw6LJ8G0Pc67TPpfuLNPHi6H_cedo_8zvewduumfzhROyU79iYdrURp1j1mOYXXpSKXLN3ZDuQvKZ5v4xeGHoceXVcejIqx0wHSm0CVDw8xO0gfAREwsVQ8dSefO0-b2UPwschI_XShlfsHdkv5eqLmskzaiGjYkYhAHSFaT7n-Uen43KW7SYbEIlKsPmRUfecs5uEJBj6bEh3zFpJXQv3goiLTQjCbHSVsXY_ZgUOmZ73rsNjkpbDkvlRDaFTzBt5f2i1Y8X81XFPOGWz9QT-N_K3oagnsGnPZ5zVM4l8QAX3MvsBSZ7rwOzVkYom2uUFiUOHJ2wWhJMMi6l2-aOjcBWisjHXzkABMbGaNBhKE8SBGacIDd1OtDZ19NL5NwC2oQ1OxmiyLtER4ikgqlTkiS6Lxnqhkmd4N2DTmpn3XVKyElAovc993jl_zH0xITRNT16wJDOGCvMi0DXhgWM0CbZhPkRan3gr6daDyRw4ZdCvHDhAXnTRNBpuTlJqnFPCymklht9jxDjDzdnsTvVoxhVe-kPZTFz1_gSIhEshytCmAr2U5rED2lpcl8q1jVV4Xs0NHEBwHjPHQPjEA6DtvfQ30BVxbLSK6nIDrT4CFkWtT9npTXcVAC8XtAdwRyaYD9H_cGumGkCjG05GGBhHKhNj_rTu2th_DpucPW0k0A8ZYcOfncgl1HA-92EXwLESIPOQji2opwZ56sNaHZXgn5SFyUgMe3KUuJ8byVO5GgsilbbLkjp3UZOI8GLpYN6_5G69B-pMpCN26NhlAPCsgDaF1FObkk2SnrL93gnzXjiA7cRH4G7utnFiIPT3T6RsGjirIWjb9SoVhkx1KA64hHqCzYx7cCtPtXr_JS2yStkXIS9AxRxi6Rak0J_AhQTlh_89q1lDHQdOyAmJrQmgys-4iPrRsqwlcRpGkc0GZszaT7gjLgJeyKG9lYsTywk4y_p10ePdB5YJVs7wxBkbJNDsAep9TKeAwI9QPUSeHoS5p6-D0VViCbYlsLvmn_zBjTPht8_mV8df6tTWxBouG0cAn5PZAtEjRv3q9K3NxJDGlgJ840x7Nzj9sZvzyjcSomD-HQRSYZbKtQf61HBhy_ODk3-9xXrie5ya6fMfxmFxoSBrpZphmoyH0IGlQJT2VOCJF1T5fLX3qbCiDj09PRk6O_8NaTGkjR3IdBaG8IBYRevcwY1Yp1C8na8ox1Itovs9uGXQr_CBErL9avratwlaU0PP_CkTOHe9fHMsj6Frvth2GJZw4SSkJ016OhzS-pw1VKpVa0KyhOReOOTvM7kurNm9sudn0B6T45rJUFaV79n975LJmQajbg-T0omkYM7Wa1NPrcWUibM2UjOt-xOewFrNTfc_Ck5QdICZASfKxdZOpmopHK8iC8WjGyVgODYuVejD6kRPwLsVHHTitkgqDFxOVWZB8rAIsrcNp3gCKgfCyzDSE6QBZiqvEpvmBmsn4gFflwha2e7_zjeshAKqfn0GK5U_ylDuWkh8UudkZtzmoiXIlsKUPc2kPDbAghovXf_8Vdd1cErFD-JV69HjSlqs2aaSx9_eRPJtbN4mfSXDzcDIjzreDe4YCTrmntAScfSW5NOPJWfLLOitbydhXo4a9K5ONPJxCjRbpu3hp4gMYQ3ddaGfgrIDrMl5mtn_SxobrWxb14iUgluJwJ49XonjHAhn3XlKlgdM3p9umi0usXCpEaErgHZrH2wkR1UnRF-Evzhs_I1T_w8kaO26ZErZVGw4Ttj4TbJjI5YzcoKaewdvwhFO0LyN0aPm88fu3EbHAA7k3i3OoonCPPPtxeBme1laiEuyXZ62NZr6BOcC7Pddg4PmLJHOgfWwlZdYSb4fI-SxXALgt4fft2qq_bT2XNLdq895I5OCjedmGLDjekuosyuFBmxMrSlgRZj044QvJyJ5oKcCvc-wXTCRj1ZnywKRyO7KT4EOMQsm5CH6wXK32CLv5cc1Og97iKCzr82q4phibgfmEueRZ420Z6PmFzW3HuxEh1HbD5_F3MIOn1navXgPVCYMlLNbhjiGVYzmeGTxoR07ex2hcwQf-ESh1P5i7KjgZPn5kL-w1tB7GVevKzEMms5CvV_TeF9sN-dvDJS0xsmTJ2ZMQNg6j0jNnGm079Y7wzo5ljP-Kmlk8jRGcejgvYl2IERoMp567qTIgZdDdRTHRDpRMz4n0mI5b0aXsk7gi-vVCPcUl.HJcbgBLMFO0qOcDwl8jPfw"

# Accessing environment variables
library_id = os.environ.get("LIBRARY_ID")
api_key = os.environ.get("API_KEY")
library_type = os.environ.get("LIBRARY_TYPE")
token = os.environ.get("TOKEN")

# Printing out the values to verify
print("Library ID:", library_id)
print("API Key:", api_key)
print("Library Type:", library_type)
print("Token:", token)




chat_args = {
    "session_token":token,
    # "conversation_id":'258d2f9d-9932-4d1e-9e0a-40d18e28ae22',
    "chat_id": "pdf"
}

zt=Zotero(
library_id = library_id,
    api_key=api_key,
    library_type =library_type,
    chat_args=chat_args)
collection = zt.get_or_update_collection(collection_name="lawful evidence",update=True)
# collection2 = zt.get_or_update_collection(collection_name="cyber due dilligence",update=False)
collection3 = zt.get_or_update_collection(collection_name="state responsibility",update=False)

zt.update_all_zotero_item_tags(item_id="4WD89ZHE",aim="replace",index=0)

print(len(collection["items"]["papers"]))
print(len(collection["items"]["papers"].keys()))
for paper in collection["items"]["papers"]:
    print(collection["items"]["papers"][paper])
print(collection["items"]["papers"])

# for n,notes in enumerate(collection["items"]):
#
#     print(n,notes["notes"],sep="\n")