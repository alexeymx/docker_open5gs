from cgrateshttapi import CGRateS


CGRateS_Obj = CGRateS("34.27.10.163", 2080)

Create_Account_JSON = {
    "method": "ApierV2.SetAccount",
    "params": [
        {
            "Account": "525570714941"
        }
    ]
}
print(CGRateS_Obj.SendData(Create_Account_JSON))

# Get Account Info (We'll see the Account we just created, but no balances)
print(CGRateS_Obj.SendData({"method": "ApierV2.GetAccount", "params": [
              { "Account": "525570714941"}]}))