# Faroswap BOT
Faroswap BOT

- Link : [Faroswap](https://faroswap.xyz/)
- Connect Same Wallet With Pharos

## Features

  - Auto Get Account Information
  - Auto Run With [Proxyscrape Free Proxy](https://proxyscrape.com/free-proxy-list) - `Choose 1`
  - Auto Run With Private Proxy - `Choose 2`
  - Auto Run Without Proxy - `Choose 3`
  - Auto Deposit PHRS to WPHRS
  - Auto Withdraw WPHRS to PHRS
  - Auto Swap With Random Pairs
  - Auto Add Liquidity Pool
  - Multi Accounts

### Note: Other features will be updated soon.

## Requiremnets

- Make sure you have Python3.9 or higher installed and pip.

## Instalation

1. **Clone The Repositories:**
   ```bash
   git clone https://github.com/vonssy/Faroswap-BOT.git
   ```
   ```bash
   cd Faroswap-BOT
   ```

2. **Install Requirements:**
   ```bash
   pip install -r requirements.txt #or pip3 install -r requirements.txt
   ```

### Note: Check your web3 and eth-account library version first. If not same with version in requirements.txt, u must uninstall that library.
- **Check Library Version**
  ```bash
    pip show libary_name
  ```
- **Uninstall Library**
  ```bash
    pip uninstall libary_name
  ```
- **Install Library With Version**
  ```bash
    pip install libary_name==version
  ```

## Configuration

### Screenshots

<div style="text-align: center;">
  <img src="images/image1.png" alt="Image" width="500"/>
</div>
<div style="text-align: center;">
  <img src="images/image2.png" alt="Image" width="500"/>
</div>
<div style="text-align: center;">
  <img src="images/image3.png" alt="Image" width="500"/>
</div>
<div style="text-align: center;">
  <img src="images/image4.png" alt="Image" width="500"/>
</div>
<div style="text-align: center;">
  <img src="images/image5.png" alt="Image" width="500"/>
</div>
<div style="text-align: center;">
  <img src="images/image6.png" alt="Image" width="500"/>
</div>
<div style="text-align: center;">
  <img src="images/image7.png" alt="Image" width="500"/>
</div>

- **pools.json:** You will find the file `pools.json` inside the project directory. Make sure `pools.json` contains data that matches the format expected by the script. Here are examples of file formats:
  ```json
    [    
        {
            "USDC_USDT": "Your USDC_USDT PMM Pool Address",
            "USDT_USDC": "Your USDT_USDC PMM Pool Address"
        }
    ]
  ```
  
- **accounts.txt:** You will find the file `accounts.txt` inside the project directory. Make sure `accounts.txt` contains data that matches the format expected by the script. Here are examples of file formats:
  ```bash
    your_private_key_1
    your_private_key_2
  ```

- **proxy.txt:** You will find the file `proxy.txt` inside the project directory. Make sure `proxy.txt` contains data that matches the format expected by the script. Here are examples of file formats:
  ```bash
    ip:port # Default Protcol HTTP.
    protocol://ip:port
    protocol://user:pass@ip:port
  ```

## Run

```bash
python bot.py #or python3 bot.py
```

## Buy Me a Coffee

- **EVM:** 0xe3c9ef9a39e9eb0582e5b147026cae524338521a
- **TON:** UQBEFv58DC4FUrGqinBB5PAQS7TzXSm5c1Fn6nkiet8kmehB
- **SOL:** E1xkaJYmAFEj28NPHKhjbf7GcvfdjKdvXju8d8AeSunf
- **SUI:** 0xa03726ecbbe00b31df6a61d7a59d02a7eedc39fe269532ceab97852a04cf3347

Thank you for visiting this repository, don't forget to contribute in the form of follows and stars.
If you have questions, find an issue, or have suggestions for improvement, feel free to contact me or open an *issue* in this GitHub repository.

**vonssy**