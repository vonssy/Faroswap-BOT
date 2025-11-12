from web3 import Web3
from web3.exceptions import TransactionNotFound
from eth_account import Account
from aiohttp import ClientResponseError, ClientSession, ClientTimeout, BasicAuth
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, random, time, re, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class Faroswap:
    def __init__(self) -> None:
        self.BASE_API = "https://api.dodoex.io"
        self.RPC_URL = "https://atlantic.dplabs-internal.com/"
        self.EXPLORER = "https://atlantic.pharosscan.xyz/tx/"
        self.PHRS_CONTRACT_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
        self.USDT_CONTRACT_ADDRESS = "0xE7E84B8B4f39C507499c40B4ac199B050e2882d5"
        self.USDC_CONTRACT_ADDRESS = "0xE0BE08c77f415F577A1B3A9aD7a1Df1479564ec8"
        self.DODO_APPROVE_ADDRESS = "0x4Cf317b8918FbE8A890c01eDAb7d548555Ac2cE9"
        self.DODO_ROUTE_PROXY_ADDRESS = "0x819829e5CF6e19F9fED92F6b4CC1edF45a2cC4A2"
        self.POSITION_MANAGER_ADDRESS = "0x1c430d84DD6185b1Ea2d4693e0033799d193542f"
        self.CONTRACT_ABI = [
            {
                "inputs": [
                    { "internalType": "address", "name": "owner", "type": "address" },
                    { "internalType": "address", "name": "spender", "type": "address" }
                ],
                "name": "allowance",
                "outputs": [
                    { "internalType": "uint256", "name": "", "type": "uint256" }
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    { "internalType": "address", "name": "spender", "type": "address" },
                    { "internalType": "uint256", "name": "value", "type": "uint256" }
                ],
                "name": "approve",
                "outputs": [
                    { "internalType": "bool", "name": "", "type": "bool" }
                ],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    { "internalType": "address", "name": "account", "type": "address" }
                ],
                "name": "balanceOf",
                "outputs": [
                    { "internalType": "uint256", "name": "", "type": "uint256" }
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [],
                "name": "decimals",
                "outputs": [
                    { "internalType": "uint8", "name": "", "type": "uint8" }
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    {
                        "components": [
                            { "internalType": "address", "name": "token0", "type": "address" },
                            { "internalType": "address", "name": "token1", "type": "address" },
                            { "internalType": "uint24", "name": "fee", "type": "uint24" },
                            { "internalType": "int24", "name": "tickLower", "type": "int24" },
                            { "internalType": "int24", "name": "tickUpper", "type": "int24" },
                            { "internalType": "uint256", "name": "amount0Desired", "type": "uint256" },
                            { "internalType": "uint256", "name": "amount1Desired", "type": "uint256" },
                            { "internalType": "uint256", "name": "amount0Min", "type": "uint256" },
                            { "internalType": "uint256", "name": "amount1Min", "type": "uint256" },
                            { "internalType": "address", "name": "recipient", "type": "address" },
                            { "internalType": "uint256", "name": "deadline", "type": "uint256" }
                        ],
                        "internalType": "struct INonfungiblePositionManager.MintParams",
                        "name": "params",
                        "type": "tuple"
                    }
                ],
                "name": "mint",
                "outputs": [
                    { "internalType": "uint256", "name": "tokenId", "type": "uint256" },
                    { "internalType": "uint128", "name": "liquidity", "type": "uint128" },
                    { "internalType": "uint256", "name": "amount0", "type": "uint256" },
                    { "internalType": "uint256", "name": "amount1", "type": "uint256" }
                ],
                "stateMutability": "payable",
                "type": "function"
            }
        ]
        self.HEADERS = {}
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.pool_addresses = []
        self.used_nonce = {}
        self.swap_count = 0
        self.phrs_swap_amount = 0
        self.usdt_swap_amount = 0
        self.usdc_swap_amount = 0
        self.liquidity_count = 0
        self.liquidity_amount = 0
        self.min_delay = 0
        self.max_delay = 0

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Faroswap{Fore.BLUE + Style.BRIGHT} Auto BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    async def load_proxies(self):
        filename = "proxy.txt"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                return
            with open(filename, 'r') as f:
                self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, token):
        if token not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[token] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[token]

    def rotate_proxy_for_account(self, token):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[token] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def build_proxy_config(self, proxy=None):
        if not proxy:
            return None, None, None

        if proxy.startswith("socks"):
            connector = ProxyConnector.from_url(proxy)
            return connector, None, None

        elif proxy.startswith("http"):
            match = re.match(r"http://(.*?):(.*?)@(.*)", proxy)
            if match:
                username, password, host_port = match.groups()
                clean_url = f"http://{host_port}"
                auth = BasicAuth(username, password)
                return None, clean_url, auth
            else:
                return None, proxy, None

        raise Exception("Unsupported Proxy Type.")
    
    def generate_address(self, account: str):
        try:
            account = Account.from_key(account)
            address = account.address
            
            return address
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Generate Address Failed {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}                  "
            )
            return None
        
    def mask_account(self, account):
        try:
            mask_account = account[:6] + '*' * 6 + account[-6:]
            return mask_account
        except Exception as e:
            return None
        
    def generate_swap_option(self):
        pairs = [
            ("PHRS", "USDT", self.PHRS_CONTRACT_ADDRESS, self.USDT_CONTRACT_ADDRESS, self.phrs_swap_amount),
            ("PHRS", "USDC", self.PHRS_CONTRACT_ADDRESS, self.USDC_CONTRACT_ADDRESS, self.phrs_swap_amount),
            ("USDT", "PHRS", self.USDT_CONTRACT_ADDRESS, self.PHRS_CONTRACT_ADDRESS, self.usdt_swap_amount),
            ("USDT", "USDC", self.USDT_CONTRACT_ADDRESS, self.USDC_CONTRACT_ADDRESS, self.usdt_swap_amount),
            ("USDC", "PHRS", self.USDC_CONTRACT_ADDRESS, self.PHRS_CONTRACT_ADDRESS, self.usdc_swap_amount),
            ("USDC", "USDT", self.USDC_CONTRACT_ADDRESS, self.USDT_CONTRACT_ADDRESS, self.usdc_swap_amount)
        ]

        from_ticker, to_ticker, from_token, to_token, amount_in = random.choice(pairs)

        return from_ticker, to_ticker, from_token, to_token, amount_in

    async def get_web3_with_check(self, address: str, use_proxy: bool, retries=3, timeout=60):
        request_kwargs = {"timeout": timeout}

        proxy = self.get_next_proxy_for_account(address) if use_proxy else None

        if use_proxy and proxy:
            request_kwargs["proxies"] = {"http": proxy, "https": proxy}

        for attempt in range(retries):
            try:
                web3 = Web3(Web3.HTTPProvider(self.RPC_URL, request_kwargs=request_kwargs))
                web3.eth.get_block_number()
                return web3
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(3)
                    continue
                raise Exception(f"Failed to Connect to RPC: {str(e)}")
            
    async def send_raw_transaction_with_retries(self, account, web3, tx, retries=5):
        for attempt in range(retries):
            try:
                signed_tx = web3.eth.account.sign_transaction(tx, account)
                raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
                tx_hash = web3.to_hex(raw_tx)
                return tx_hash
            except TransactionNotFound:
                pass
            except Exception as e:
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}   Message  :{Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT} [Attempt {attempt + 1}] Send TX Error: {str(e)} {Style.RESET_ALL}"
                )
            await asyncio.sleep(2 ** attempt)
        raise Exception("Transaction Hash Not Found After Maximum Retries")

    async def wait_for_receipt_with_retries(self, web3, tx_hash, retries=5):
        for attempt in range(retries):
            try:
                receipt = await asyncio.to_thread(web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
                return receipt
            except TransactionNotFound:
                pass
            except Exception as e:
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}   Message  :{Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT} [Attempt {attempt + 1}] Wait for Receipt Error: {str(e)} {Style.RESET_ALL}"
                )
            await asyncio.sleep(2 ** attempt)
        raise Exception("Transaction Receipt Not Found After Maximum Retries")
        
    async def get_token_balance(self, address: str, contract_address: str, use_proxy: bool, retries=5):
        for attempt in range(retries):
            try:
                web3 = await self.get_web3_with_check(address, use_proxy)

                if contract_address == self.PHRS_CONTRACT_ADDRESS:
                    balance = web3.eth.get_balance(address)
                    decimals = 18
                else:
                    token_contract = web3.eth.contract(address=web3.to_checksum_address(contract_address), abi=self.CONTRACT_ABI)
                    balance = token_contract.functions.balanceOf(address).call()
                    decimals = token_contract.functions.decimals().call()

                token_balance = balance / (10 ** decimals)

                return token_balance
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(3)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Message  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                return None
        
    async def approving_token(self, account: str, address: str, spender: str, asset_address: str, amount_to_wei: int, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)
            
            token_contract = web3.eth.contract(address=asset_address, abi=self.CONTRACT_ABI)

            allowance = token_contract.functions.allowance(address, spender).call()
            if allowance < amount_to_wei:
                approve_data = token_contract.functions.approve(spender, 2**256 - 1)
                estimated_gas = approve_data.estimate_gas({"from": address})

                max_priority_fee = web3.to_wei(1, "gwei")
                max_fee = max_priority_fee

                approve_tx = approve_data.build_transaction({
                    "from": web3.to_checksum_address(address),
                    "gas": int(estimated_gas * 1.2),
                    "maxFeePerGas": int(max_fee),
                    "maxPriorityFeePerGas": int(max_priority_fee),
                    "nonce": self.used_nonce[address],
                    "chainId": web3.eth.chain_id,
                })

                tx_hash = await self.send_raw_transaction_with_retries(account, web3, approve_tx)
                receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)
                block_number = receipt.blockNumber
                self.used_nonce[address] += 1

                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Approve  :{Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT} Success {Style.RESET_ALL}                      "
                )
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Block    :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {block_number} {Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Tx Hash  :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {tx_hash} {Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Explorer :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {self.EXPLORER}{tx_hash} {Style.RESET_ALL}"
                )
                await self.print_timer()

            return True
        except Exception as e:
            raise Exception(f"Approving Token Contract Failed: {str(e)}")
        
    async def perform_swap(self, account: str, address: str, from_token: str, to_token: str, amount_in: float, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            decimals = 18 if from_token == self.PHRS_CONTRACT_ADDRESS else 6

            amount_in_wei = int(amount_in * 10**decimals)

            spender = web3.to_checksum_address(self.DODO_APPROVE_ADDRESS)
            asset_address = web3.to_checksum_address(from_token)
            router_address = web3.to_checksum_address(self.DODO_ROUTE_PROXY_ADDRESS)

            if from_token != self.PHRS_CONTRACT_ADDRESS:
                await self.approving_token(account, address, spender, asset_address, amount_in_wei, use_proxy)

            route = await self.get_dodo_route(address, from_token, to_token, amount_in_wei, use_proxy)
            if not route: return None, None

            value = route["data"]["value"]
            calldata = route["data"]["data"]
            gas_limit = route["data"]["gasLimit"]

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee
            
            swap_tx = {
                "from": web3.to_checksum_address(address),
                "to": router_address,
                "value": int(value),
                "data": calldata,
                "gas": int(gas_limit),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id
            }

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, swap_tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)
            block_number = receipt.blockNumber
            self.used_nonce[address] += 1

            return tx_hash, block_number
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Message  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None, None
        
    async def perform_liquidity(self, account: str, address: str, amount: float, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            amount0_desired = int(amount * (10**6))
            amount1_desired = amount0_desired
            amount0_min = int(amount0_desired * (1 - 0.005))
            amount1_min = int(amount1_desired * (1 - 0.005))
            deadline = int(time.time()) + 600

            router_address = web3.to_checksum_address(self.POSITION_MANAGER_ADDRESS)
            token0 = web3.to_checksum_address(self.USDC_CONTRACT_ADDRESS)
            token1 = web3.to_checksum_address(self.USDT_CONTRACT_ADDRESS)

            await self.approving_token(account, address, router_address, token0, amount0_desired, use_proxy)
            await self.approving_token(account, address, router_address, token1, amount1_desired, use_proxy)

            mint_params = (
                token0,
                token1,
                500,
                -887270,
                887270,
                amount0_desired,
                amount1_desired,
                amount0_min,
                amount1_min,
                web3.to_checksum_address(address),
                deadline
            )

            token_contract = web3.eth.contract(address=router_address, abi=self.CONTRACT_ABI)

            mint_data = token_contract.functions.mint(mint_params)

            estimated_gas = mint_data.estimate_gas({"from": address})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            mint_tx = mint_data.build_transaction({
                "from": web3.to_checksum_address(address),
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            })

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, mint_tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)
            block_number = receipt.blockNumber
            self.used_nonce[address] += 1

            return tx_hash, block_number
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Message  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None, None
        
    def print_swap_question(self):
        while True:
            try:
                swap_count = int(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Swap Count -> {Style.RESET_ALL}").strip())
                if swap_count > 0:
                    self.swap_count = swap_count
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Swap Count must be > 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

        while True:
            try:
                phrs_swap_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Swap Amount [PHRS] -> {Style.RESET_ALL}").strip())
                if phrs_swap_amount > 0:
                    self.phrs_swap_amount = phrs_swap_amount
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Amount must be > 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a float or decimal number.{Style.RESET_ALL}")

        while True:
            try:
                usdt_swap_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Swap Amount [USDT] -> {Style.RESET_ALL}").strip())
                if usdt_swap_amount > 0:
                    self.usdt_swap_amount = usdt_swap_amount
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Amount must be > 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a float or decimal number.{Style.RESET_ALL}")

        while True:
            try:
                usdc_swap_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Swap Amount [USDC] -> {Style.RESET_ALL}").strip())
                if usdc_swap_amount > 0:
                    self.usdc_swap_amount = usdc_swap_amount
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Amount must be > 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a float or decimal number.{Style.RESET_ALL}")

    def print_liquidity_question(self):
        while True:
            try:
                liquidity_count = int(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Add Liquidity Count -> {Style.RESET_ALL}").strip())
                if liquidity_count > 0:
                    self.liquidity_count = liquidity_count
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Add Liquidity Count must be > 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

        while True:
            try:
                liquidity_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Liquidity Amount [USDC/USDT] -> {Style.RESET_ALL}").strip())
                if liquidity_amount > 0:
                    self.liquidity_amount = liquidity_amount
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Liquidity Amount must be > 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a float or decimal number.{Style.RESET_ALL}")

    def print_delay_question(self):
        while True:
            try:
                min_delay = int(input(f"{Fore.YELLOW + Style.BRIGHT}Min Delay For Each Tx -> {Style.RESET_ALL}").strip())
                if min_delay >= 0:
                    self.min_delay = min_delay
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Min Delay must be >= 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

        while True:
            try:
                max_delay = int(input(f"{Fore.YELLOW + Style.BRIGHT}Max Delay For Each Tx -> {Style.RESET_ALL}").strip())
                if max_delay >= min_delay:
                    self.max_delay = max_delay
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Max Delay must be >= Min Delay.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")
         
    async def print_timer(self):
        for remaining in range(random.randint(self.min_delay, self.max_delay), 0, -1):
            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Wait For{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {remaining} {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Seconds For Next Tx...{Style.RESET_ALL}",
                end="\r",
                flush=True
            )
            await asyncio.sleep(1)

    def print_question(self):
        while True:
            try:
                print(f"{Fore.GREEN + Style.BRIGHT}Select Option:{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}1. Random Swap{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Add Liquidity{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}3. Run All Features{Style.RESET_ALL}")
                option = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2/3] -> {Style.RESET_ALL}").strip())

                if option in [1, 2, 3]:
                    option_type = (
                        "Random Swap" if option == 1 else
                        "Add Liquidity" if option == 2 else
                        "Run All Features"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{option_type} Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2, or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2, or 3).{Style.RESET_ALL}")

        if option == 1:
            self.print_swap_question()
            self.print_delay_question()

        elif option == 2:
            self.print_liquidity_question()
            self.print_delay_question()

        elif option == 3:
            self.print_swap_question()
            self.print_liquidity_question()
            self.print_delay_question()

        while True:
            try:
                print(f"{Fore.WHITE + Style.BRIGHT}1. Run With Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Run Without Proxy{Style.RESET_ALL}")
                proxy_choice = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2] -> {Style.RESET_ALL}").strip())

                if proxy_choice in [1, 2]:
                    proxy_type = (
                        "With" if proxy_choice == 2 else 
                        "Without"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}Run {proxy_type} Proxy Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1 or 2.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1 or 2).{Style.RESET_ALL}")

        rotate_proxy = False
        if proxy_choice == 1:
            while True:
                rotate_proxy = input(f"{Fore.BLUE + Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Style.RESET_ALL}").strip()

                if rotate_proxy in ["y", "n"]:
                    rotate_proxy = rotate_proxy == "y"
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")

        return option, proxy_choice, rotate_proxy
    
    async def check_connection(self, proxy_url=None):
        connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=10)) as session:
                async with session.get(url="https://api.ipify.org?format=json", proxy=proxy, proxy_auth=proxy_auth) as response:
                    response.raise_for_status()
                    return True
        except (Exception, ClientResponseError) as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Connection Not 200 OK {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None
        
    async def get_dodo_route(self, address: str, from_token: str, to_token: str, amount_in: int, use_proxy: bool, retries=5):
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://faroswap.xyz",
            "Referer": "https://faroswap.xyz/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "User-Agent": FakeUserAgent().random
        }

        for attempt in range(retries):
            deadline = int(time.time()) + 600
            url = f"{self.BASE_API}/route-service/v2/widget/getdodoroute?chainId=688689&deadLine={deadline}&apikey=a37546505892e1a952&slippage=3.225&source=dodoV2AndMixWasm&toTokenAddress={to_token}&fromTokenAddress={from_token}&userAddr={address}&estimateGas=true&fromAmount={amount_in}"
            proxy_url = self.get_next_proxy_for_account(address) if use_proxy else None
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        result = await response.json()
                        if result.get("status") != 200:
                            err_msg = result.get("data", "Quote Not Available")
                            raise ValueError(err_msg)

                        return result
            except (Exception, ClientResponseError) as e:
                if attempt < retries:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}   Message  :{Style.RESET_ALL}"
                        f"{Fore.RED+Style.BRIGHT} Fetch Dodo Route Failed: {Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT}{str(e)} [Attempt: {attempt+1}/{retries}]{Style.RESET_ALL}"
                    )
                    await asyncio.sleep(3)
                    continue
                return None
    
    async def process_check_connection(self, address: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Proxy     :{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {proxy} {Style.RESET_ALL}"
            )

            is_valid = await self.check_connection(proxy)
            if not is_valid:
                if rotate_proxy:
                    proxy = self.rotate_proxy_for_account(address)
                    await asyncio.sleep(1)
                    continue

                return False
            
            return True
        
    async def process_perform_swap(self, account: str, address: str, from_token: str, to_token: str, amount_in: float, use_proxy: bool):
        tx_hash, block_number = await self.perform_swap(account, address, from_token, to_token, amount_in, use_proxy)
        if tx_hash and block_number:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Status   :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} Success {Style.RESET_ALL}                      "
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Block    :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {block_number} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Tx Hash  :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {tx_hash} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Explorer :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {self.EXPLORER}{tx_hash} {Style.RESET_ALL}"
            )
        else:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Status   :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Perform On-Chain Failed {Style.RESET_ALL}"
            )

    async def process_perform_liquidity(self, account: str, address: str, amount: float, use_proxy: bool):
        tx_hash, block_number = await self.perform_liquidity(account, address, amount, use_proxy)
        if tx_hash and block_number:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Status   :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} Success {Style.RESET_ALL}                      "
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Block    :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {block_number} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Tx Hash  :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {tx_hash} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Explorer :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {self.EXPLORER}{tx_hash} {Style.RESET_ALL}"
            )
        else:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Status   :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Perform On-Chain Failed {Style.RESET_ALL}"
            )

    async def process_option_1(self, account: str, address: str, use_proxy):
        self.log(f"{Fore.CYAN+Style.BRIGHT}Swap      :{Style.RESET_ALL}                      ")
        for i in range(self.swap_count):
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT}Swap{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {i+1} Of {self.swap_count} {Style.RESET_ALL}                           "
            )

            from_ticker, to_ticker, from_token, to_token, amount_in = self.generate_swap_option()

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Option   :{Style.RESET_ALL}"
                f"{Fore.BLUE+Style.BRIGHT} {from_ticker} to {to_ticker} {Style.RESET_ALL}"
            )

            balance = await self.get_token_balance(address, from_token, use_proxy)

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Balance  :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {balance} {from_ticker} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Amount   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {amount_in} {from_ticker} {Style.RESET_ALL}"
            )

            if balance is None:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Status   :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Fetch {from_ticker} Token Balance Failed {Style.RESET_ALL}"
                )
                continue

            if balance <=  amount_in:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Status   :{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} Insufficient {from_ticker} Token Balance {Style.RESET_ALL}"
                )
                continue
            
            await self.process_perform_swap(account, address, from_token, to_token, amount_in, use_proxy)
            await self.print_timer()

    async def process_option_2(self, account: str, address: str, use_proxy):
        self.log(f"{Fore.CYAN+Style.BRIGHT}Liquidity :{Style.RESET_ALL}                      ")
        for i in range(self.liquidity_count):
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT}Liquidity{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {i+1} Of {self.liquidity_count} {Style.RESET_ALL}                           "
            )

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}   Option   :{Style.RESET_ALL}"
                f"{Fore.BLUE+Style.BRIGHT} USDC/USDT {Style.RESET_ALL}"
            )

            self.log(f"{Fore.CYAN+Style.BRIGHT}   Amount   :{Style.RESET_ALL}")
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}      ● {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{self.liquidity_amount} USDC{Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}      ● {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{self.liquidity_amount} USDT{Style.RESET_ALL}"
            )

            balance0 = await self.get_token_balance(address, self.USDC_CONTRACT_ADDRESS, use_proxy)
            balance1 = await self.get_token_balance(address, self.USDT_CONTRACT_ADDRESS, use_proxy)

            self.log(f"{Fore.CYAN+Style.BRIGHT}   Balance  :{Style.RESET_ALL}")
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}      ● {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{balance0} USDC{Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}      ● {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{balance1} USDT{Style.RESET_ALL}"
            )

            if balance0 is None:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Status   :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Fetch USDC Token Balance Failed {Style.RESET_ALL}"
                )
                continue

            if balance1 is None:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Status   :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Fetch USDT Token Balance Failed {Style.RESET_ALL}"
                )
                continue

            if balance0 <  self.liquidity_amount:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Status   :{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} Insufficient USDC Token Balance {Style.RESET_ALL}"
                )
                return

            if balance1 <  self.liquidity_amount:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Status   :{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} Insufficient USDT Token Balance {Style.RESET_ALL}"
                )
                return
            
            await self.process_perform_liquidity(account, address, self.liquidity_amount, use_proxy)
            await self.print_timer()

    async def process_accounts(self, account: str, address: str, option: int, use_proxy: bool, rotate_proxy: bool):
        is_valid = await self.process_check_connection(address, use_proxy, rotate_proxy)
        if is_valid:
            try:
                web3 = await self.get_web3_with_check(address, use_proxy)
            except Exception as e:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Web3 Not Connected {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
                return
            
            self.used_nonce[address] = web3.eth.get_transaction_count(address, "pending")
            
            if option == 1:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Option    :{Style.RESET_ALL}"
                    f"{Fore.BLUE+Style.BRIGHT} Random Swap {Style.RESET_ALL}"
                )
                await self.process_option_1(account, address, use_proxy)

            elif option == 2:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Option    :{Style.RESET_ALL}"
                    f"{Fore.BLUE+Style.BRIGHT} Add Liquidity {Style.RESET_ALL}"
                )
                await self.process_option_2(account, address, use_proxy)

            elif option == 3:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Option    :{Style.RESET_ALL}"
                    f"{Fore.BLUE+Style.BRIGHT} Run All Features {Style.RESET_ALL}"
                )

                await self.process_option_1(account, address, use_proxy)
                await asyncio.sleep(5)

                await self.process_option_2(account, address, use_proxy)
                await asyncio.sleep(5)

    async def main(self):
        try:
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]

            option, proxy_choice, rotate_proxy = self.print_question()

            while True:
                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
                )

                use_proxy = True if proxy_choice == 1 else False
                if use_proxy:
                    await self.load_proxies()
                
                separator = "=" * 25
                for account in accounts:
                    if account:
                        address = self.generate_address(account)

                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(address)} {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                        )

                        if not address:
                            self.log(
                                f"{Fore.CYAN + Style.BRIGHT}Status    :{Style.RESET_ALL}"
                                f"{Fore.RED + Style.BRIGHT} Invalid Private Key or Library Version Not Supported {Style.RESET_ALL}"
                            )
                            continue

                        await self.process_accounts(account, address, option, use_proxy, rotate_proxy)
                        await asyncio.sleep(3)

                self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*72)
                seconds = 24 * 60 * 60
                while seconds > 0:
                    formatted_time = self.format_seconds(seconds)
                    print(
                        f"{Fore.CYAN+Style.BRIGHT}[ Wait for{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT}... ]{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.BLUE+Style.BRIGHT}All Accounts Have Been Processed.{Style.RESET_ALL}",
                        end="\r"
                    )
                    await asyncio.sleep(1)
                    seconds -= 1

        except FileNotFoundError:
            self.log(f"{Fore.RED}File 'accounts.txt' Not Found.{Style.RESET_ALL}")
            return
        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e

if __name__ == "__main__":
    try:
        bot = Faroswap()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Faroswap - BOT{Style.RESET_ALL}                                       "                              
        )