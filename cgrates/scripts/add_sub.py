from cgrateshttapi import CGRateS


CGRateS_Obj = CGRateS("34.27.10.163", 2080)

Balance = CGRateS_Obj.SendData({"jsonrpc":"2.0","method":"ApierV1.GetAccount","params":[{"TPid":"cgrates.org",  "Account": "525570714941"}]})


print(Balance)

Create_Account_JSON = {
    "method": "ApierV2.SetAccount",
    "params": [
        {
            "Account": "525570714941",
            "Tenant": "cgrates.org",
            "Type": "*prepaid"
        }
    ]
}

Create_Voice_Balance_JSON = {
    "method": "ApierV1.SetBalance",
    "params": [
        {
            "Tenant": "cgrates.org",
            "Account": "525570714941",
            "BalanceType": "*voice",
            "Categories": "*any",
            "Balance": {
                "ID": "voice_national_balance",
                "Value": "5m",
                "Weight": 25,
                "DestinationIDs": "Dest_AU_Fixed",
            }
        }
    ]
}
CGRateS_Obj.SendData(Create_Voice_Balance_JSON)

CGRateS_Obj.SendData(Create_Voice_Balance_JSON)

Create_Voice_Balance_JSON = {
    "method": "ApierV1.SetBalance",
    "params": [
        {
            "Tenant": "cgrates.org",
            "Account": "525570714941",
            "BalanceType": "*data",
            "BalanceTag": "INTERNET",
            "Categories": "*any",
            "BalanceCategory": "data",
            "Balance": {
                "ID": "internet",
                "Value": 500,
                "Weight": 25,
                "DestinationIDs": "internet",
                "RatingSubject": "RatingPlan_DefaultData",
            }
        }
    ]
}
CGRateS_Obj.SendData(Create_Voice_Balance_JSON)

CGRateS_Obj.SendData({'method':'ApierV2.SetTPDestination','params':[{"TPid":"cgrates.org","ID":"Dest_AU_Fixed","Prefixes":["612", "613", "617", "618"]}]})
CGRateS_Obj.SendData({'method':'ApierV2.SetTPDestination','params':[{"TPid":"cgrates.org","ID":"Dest_AU_Mobile","Prefixes":["614"]}]})
CGRateS_Obj.SendData({'method':'ApierV2.SetTPDestination','params':[{"TPid":"cgrates.org","ID":"Dest_AU_TollFree","Prefixes":["6113", "6118"]}]})
CGRateS_Obj.SendData({'method':'ApierV2.SetTPDestination','params':[{"TPid":"cgrates.org","ID":"internet"}]})

CGRateS_Obj.SendData({"method":"APIerSv1.SetChargerProfile","params":[{"Tenant":"cgrates.org","ID":"DEFAULT","FilterIDs":[],"AttributeIDs":["*none"],"Weight":0}]})



CGRateS_Obj.SendData({"method": "ApierV1.SetTPDestinationRate", "params": \
    [{"ID": "DestinationRate_AU", "TPid": "cgrates.org", "DestinationRates": \
        [ {"DestinationId": "internet", "RateId": "internet_national", "Rate": None, "RoundingMethod": "*up", "RoundingDecimals": 4, "MaxCost": 0, "MaxCostStrategy": ""} ]\
    }]})

CGRateS_Obj.SendData({"method": "ApierV1.SetTPDestinationRate", "params": \
    [{"ID": "internet", "TPid": "cgrates.org", "DestinationRates": \
        [ {"DestinationId": "internet", "RateId": "internet_national", "Rate": None, "RoundingMethod": "*up", "RoundingDecimals": 4, "MaxCost": 0, "MaxCostStrategy": ""} ]\
    }]})

TPDestinationRates = CGRateS_Obj.SendData({"jsonrpc":"2.0","method":"ApierV1.GetTPDestinationRateIds","params":[{"TPid":"cgrates.org"}]})['result']
for TPDestinationRate in TPDestinationRates:
    print(TPDestinationRate)


TPRatingPlans = CGRateS_Obj.SendData({
    "id": 3,
    "method": "APIerSv1.SetTPRatingPlan",
    "params": [
        {
            "TPid": "cgrates.org",
            "ID": "RatingPlan_DefaultData",
            "RatingPlanBindings": [
                {
                    "DestinationRatesId": "internet",
                    "TimingId": "*any",
                    "Weight": 10
                }
            ]
        }
    ]
})

print("TPRatingPlans: ")
print(TPRatingPlans)



RatingPlan_VoiceCalls = CGRateS_Obj.SendData(
    {"jsonrpc": "2.0", "method": "ApierV1.GetTPRatingPlanIds", "params": [{"TPid": "cgrates.org"}]})
print("Rating plans: ", RatingPlan_VoiceCalls)


#Create RatingProfile
print(CGRateS_Obj.SendData({
    "method": "APIerSv1.SetRatingProfile",
    "params": [
        {
            "TPid": "RatingProfile_Data",
            "Overwrite": True,
            "LoadId" : "APItest",
            "Tenant": "cgrates.org",
            "Category": "data",
            "Subject": "*any",
            "RatingPlanActivations": [
                {
                    "ActivationTime": "2014-01-14T00:00:00Z",
                    "RatingPlanId": "RatingPlan_DefaultData",
                    "FallbackSubjects": ""
                }
            ]
        }
    ]
}))

print("GetTPRatingProfileIds: ")
TPRatingProfileIds = CGRateS_Obj.SendData({"jsonrpc": "2.0", "method": "ApierV1.GetRatingProfileIDs", "params": [{"TPid": "cgrates.org"}]})
print("TPRatingProfileIds: ")
