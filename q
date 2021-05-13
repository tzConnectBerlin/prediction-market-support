============================= test session starts ==============================
platform linux -- Python 3.9.5, pytest-6.2.4, py-1.10.0, pluggy-0.13.1
rootdir: /home/killua/Documents/Projects/tezos/prediction-market-contracts/wolfram-oracle
plugins: regtest-1.4.5, lazy-fixture-0.6.3, mock-3.6.1, timeout-1.4.2
collected 40 items

tests/test_account.py ..................                                 [ 45%]
tests/test_market.py .F..FF......FFFFFFFF..                              [100%]

=================================== FAILURES ===================================
______________________ test_ask_question[account1-data1] _______________________

account = {'key': 'tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3', 'name': 'mala'}
market = <src.market.Market object at 0x7ff5abdf1340>
data = ['who', 'why', 'mala', 300, 50000000, 76, ...]
questions_storage = <pytezos.contract.data.ContractData object at 0x7ff5ac52cc70>

Properties
.key		tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb
....tted datetime `%Y-%m-%dT%H:%M:%SZ` */


Helpers
.decode()
.default()
.dummy()
.encode()
.to_micheline()
.to_michelson()
stablecoin_id = 'KT1D6jo4Tv9CAjpB6jrTsDN9N5vxzLiGT4RA'

    @pytest.mark.parametrize("account,data", test_data)
    def test_ask_question(account, market, data, questions_storage, stablecoin_id):
        market_id, transaction = market.ask_question(data[0], data[1], data[2], data[3], data[4], data[5])
        auction_end = datetime.timestamp(datetime.now() + timedelta(minutes=data[5]))
        submit_transaction(transaction, error_func=print_error)
        question = questions_storage[market_id]()
        metadata = question['metadata']
        assert 'auctionRunning' in question['state']
        state = question['state']['auctionRunning']
        assert data[0] in metadata['description']
        assert data[1] in metadata['description']
        assert metadata['adjudicator'] == account["key"]
        assert metadata['currency'] == {'fa12': stablecoin_id}
>       assert state['auction_period_end'] == int(auction_end)
E       assert 1620838004 == 1620838005
E        +  where 1620838005 = int(1620838005.235819)

tests/test_market.py:49: AssertionError
---------------------------- Captured stdout setup -----------------------------
mock_function
----------------------------- Captured stdout call -----------------------------
Wait 1 seconds until block BLjoE5S8jiLvMbNqDoDZTdForshyMiwTL6EP6jz1GJrRYFAHGhL is finalized
------------------------------ Captured log call -------------------------------
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLjoE5S8jiLvMbNqDoDZTdForshyMiwTL6EP6jz1GJrRYFAHGhL is finalized
______________________ test_auction_clear[account0-data0] ______________________

transaction = <pytezos.operation.group.OperationGroup object at 0x7ff5ac310550>

Properties
.key		tz1Q3eT3kwr1hfvK49HK8YqPadNXzxdxnE...pply()
.proposals()
.result()
.reveal()
.run()
.run_operation()
.seed_nonce_revelation()
.send()
.sign()
.transaction()
count = None, tries = 3, error_func = <function print_error at 0x7ff5acdf7790>

    def submit_transaction(transaction, count=None, tries=3, error_func=None):
        """
        Submit a transaction
        """
        try:
            source = transaction.key.public_key_hash()
>           transaction_ = transaction.autofill(ttl=56)

src/utils.py:74: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <pytezos.operation.group.OperationGroup object at 0x7ff5ac310550>

Properties
.key		tz1Q3eT3kwr1hfvK49HK8YqPadNXzxdxnE...pply()
.proposals()
.result()
.reveal()
.run()
.run_operation()
.seed_nonce_revelation()
.send()
.sign()
.transaction()
gas_reserve = 100, burn_reserve = 100, counter = None, ttl = 56, fee = None
gas_limit = None, storage_limit = None, kwargs = {}
opg = <pytezos.operation.group.OperationGroup object at 0x7ff5abdf1520>

Properties
.key		tz1Q3eT3kwr1hfvK49HK8YqPadNXzxdxnE...pply()
.proposals()
.result()
.reveal()
.run()
.run_operation()
.seed_nonce_revelation()
.send()
.sign()
.transaction()
opg_with_metadata = {'contents': [{'amount': '0', 'counter': '60', 'destination': 'KT1W5yTZUT9rJYUCXRCHcY7Ko51D7Suf6PV9', 'fee': '104294', ...}], 'signature': 'sigUHx32f9wesZ1n2BWpixXz4AQaZggEtchaQNHYGRCoWNAXx45WGW2ua3apUUUAGMLPwAU41QoaFCzVSL61VaessLg4YbbP'}

    def autofill(
        self,
        gas_reserve: int = DEFAULT_GAS_RESERVE,
        burn_reserve: int = DEFAULT_BURN_RESERVE,
        counter: Optional[int] = None,
        ttl: Optional[int] = None,
        fee: Optional[int] = None,
        gas_limit: Optional[int] = None,
        storage_limit: Optional[int] = None,
        **kwargs
    ) -> 'OperationGroup':
        """Fill the gaps and then simulate the operation in order to calculate fee, gas/storage limits.
    
        :param gas_reserve: Add a safe reserve for dynamically calculated gas limit (default is 100).
        :param burn_reserve: Add a safe reserve for dynamically calculated storage limit (default is 100).
        :param counter: Override counter value (for manual handling)
        :param ttl: Number of blocks to wait in the mempool before removal (default is 5 for public network, 60 for sandbox)
        :param fee: Explicitly set fee for operation. If not set fee will be calculated depeding on results of operation dry-run.
        :param gas_limit: Explicitly set gas limit for operation. If not set gas limit will be calculated depeding on results of
            operation dry-run.
        :param storage_limit: Explicitly set storage limit for operation. If not set storage limit will be calculated depeding on
            results of operation dry-run.
        :rtype: OperationGroup
        """
        if kwargs.get('branch_offset') is not None:
            logger.warning('`branch_offset` argument is deprecated, use `ttl` instead')
            ttl = MAX_OPERATIONS_TTL - kwargs['branch_offset']
    
        opg = self.fill(counter=counter, ttl=ttl)
        opg_with_metadata = opg.run()
        if not OperationResult.is_applied(opg_with_metadata):
>           raise RpcError.from_errors(OperationResult.errors(opg_with_metadata))
E           pytezos.rpc.errors.MichelsonError: ({'id': 'proto.008-PtEdo2Zk.michelson_v1.script_rejected',
E             'kind': 'temporary',
E             'location': 333,
E             'with': {'string': 'Market auction closed'}},)

/home/killua/.cache/pypoetry/virtualenvs/prediction-market-support-mREyC6rD-py3.9/lib/python3.9/site-packages/pytezos/operation/group.py:228: MichelsonError

During handling of the above exception, another exception occurred:

account = {'key': 'tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2', 'name': 'donald'}
market = <src.market.Market object at 0x7ff5abdf1340>
data = ['who', 'why', 'donald', 300000000, 122, 0.1]
questions_storage = <pytezos.contract.data.ContractData object at 0x7ff5ac52cc70>

Properties
.key		tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb
....tted datetime `%Y-%m-%dT%H:%M:%SZ` */


Helpers
.decode()
.default()
.dummy()
.encode()
.to_micheline()
.to_michelson()
gen_cleared_markets = [{'caller_name': 'palu', 'id': 5417074671350863707}, {'caller_name': 'marty', 'id': 4627002818767176605}, {'caller_nam...2939880851}, {'caller_name': 'palu', 'id': 284766939684584008}, {'caller_name': 'palu', 'id': 106130679728296059}, ...]

    @pytest.mark.parametrize("account,data", test_data)
    def test_auction_clear(account, market, data, questions_storage, gen_cleared_markets):
        auction = random.choice(gen_cleared_markets)
        amount = rand(100)
        rate = random.randint(0, 2 ** 63)
        transaction = market.auction_clear(auction['id'], auction["caller_name"])
>       submit_transaction(transaction, error_func=print_error)

tests/test_market.py:74: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/utils.py:80: in submit_transaction
    err_message = ast.literal_eval(str(r)[1-2])
/usr/lib/python3.9/ast.py:62: in literal_eval
    node_or_string = parse(node_or_string, mode='eval')
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

source = ')', filename = '<unknown>', mode = 'eval'

    def parse(source, filename='<unknown>', mode='exec', *,
              type_comments=False, feature_version=None):
        """
        Parse the source into an AST node.
        Equivalent to compile(source, filename, mode, PyCF_ONLY_AST).
        Pass type_comments=True to get back type comments where the syntax allows.
        """
        flags = PyCF_ONLY_AST
        if type_comments:
            flags |= PyCF_TYPE_COMMENTS
        if isinstance(feature_version, tuple):
            major, minor = feature_version  # Should be a 2-tuple.
            assert major == 3
            feature_version = minor
        elif feature_version is None:
            feature_version = -1
        # Else it should be an int giving the minor version for 3.x.
>       return compile(source, filename, mode, flags,
                       _feature_version=feature_version)
E         File "<unknown>", line 1
E           )
E           ^
E       SyntaxError: unmatched ')'

/usr/lib/python3.9/ast.py:50: SyntaxError
---------------------------- Captured stdout setup -----------------------------
Wait 0 seconds until block BL4N8pY4yGhK5tXsfRoWcXNUX5oQvxVDUNg3FYQLjArnPsQykxe is finalized
Wait 0 seconds until block BLNLZ6bvgWe1UpaLQoH1PyyJeY3wePidHvZJTDpDbEFEMjW931q is finalized
Wait 1 seconds until block BLtazqX5w7LmUpFuTZBQYsmq5T2sM9HvbfgQku1FcsYeHMNFjxf is finalized
Wait 0 seconds until block BL4E8FsziFAUd3DhZLvznaPEiESocqqVGVFxoo5oPgonPmkoain is finalized
Wait 0 seconds until block BM8qBXev3hptMovBAgBhPUTvpnwfL69ujN18i72yexo5KTY7tWz is finalized
Wait 0 seconds until block BLmUBwqoPs8py6EEfLQMLu6UD7pQCtf2Pv4Sez3qQauGGeeRu2k is finalized
Wait 0 seconds until block BLEZE56YrUNSKzdjTLdeHEKuEuRyVhZhrLvzDe7fURYKN3F4woA is finalized
Wait 0 seconds until block BLoAPty2YWCAaUX9RgB8MszrDAeZQaPcErQAkmun5f26MPbX5L5 is finalized
Wait 0 seconds until block BLoktgyb2PrNNzFcRW4FrQZeoK3kVkagHEcmbjQMLwPMgBHDyzf is finalized
Wait 1 seconds until block BLh2C42YDo3wrjQBBpNiS7kgjXsfbZZZzA2cxkuMBGUbvi5npZp is finalized
Wait 0 seconds until block BLPvSa2fgAdfzwLBam8wFsvqhBB11ELU2AEw6hL9crojVHC5pSK is finalized
Wait 0 seconds until block BMBWCbDAgJvhAgj24us5R2nFvSbTUwXxSwrkW3m8kLpgzYHzcqo is finalized
Wait 1 seconds until block BL4TFrng76PGD3ASQQ51akujKk4fSoYS7vFPf8FgANzP6eXBjAw is finalized
Wait 0 seconds until block BKoskoCpUEnDSPxBQSj7zq41bzjcxkAMP8BQrA94Z8a6F6Qn6h8 is finalized
Wait 1 seconds until block BLZQRJK3voyp5UAnznsWJTG85qF9FZsmbpa5u5ywB29h3eNCTYV is finalized
Wait 0 seconds until block BLZnb31YTQFCXNi9Le21bLrtCedVRG88Y9XZP3SNoT25CA5zfg4 is finalized
Wait 0 seconds until block BMHoLXRkDGXTFFgrqqYPUUqEEs64vgio9nZrBr8x1ceaQ8mNrNs is finalized
Wait 1 seconds until block BLrTkQQbcf2Cct7FhMXCrCdjxJeQuTXQ6YqJjbDjGG6cayWdZd7 is finalized
Wait 0 seconds until block BLHF28p5zzT1KkPBT8E2fFQzJGUs8VhAEuu1qM2MgUFx3dASk6C is finalized
Wait 0 seconds until block BLG5JSssG5XVkr47LRnxXdDzeUbaYx6K2Vt8kpvUeeApd6Qxzja is finalized
Wait 1 seconds until block BMQQ51pxaAS6Pn481m83LpfVxzWCijLqAHrUDAC64fSNKbUarZ2 is finalized
Wait 0 seconds until block BKrinFrN4HvskSzYKJQy8s57KgyKnvDvMne5QeLFcPUiz3aP35y is finalized
Wait 0 seconds until block BLfnSw6t8Y6kcfp4wP4uxVHF7iLxNAJ6yKNPeRCimw9RhdwiDaP is finalized
Wait 1 seconds until block BLRsP61ea7EFeeD3hwjrKgdS8adne5M2ZpWyf3JaXn48jGGZe4u is finalized
Wait 0 seconds until block BLjXK7Xz1rXyWKCKrBpEnKLhbGZBFRXmeZAKwF8ztkFEuoVK169 is finalized
Wait 0 seconds until block BL5PoVUt8HKDE7ZZyJ1Pyb43b6h4nTT11jrjXKYQ1kGq5TuUmtz is finalized
Wait 1 seconds until block BL4gWiniQwPjQ6FHL1Yx8JvmeS66d7gDhz1VgsBrJTqhnAZEF1C is finalized
Wait 0 seconds until block BLrB6qh1KMxP6aNKWSdPqwxWbrHUj7oigXDJFEeBZF13ErYT2tm is finalized
Wait 0 seconds until block BKy3K6hjdndcDwfL4qeUUwmSBjGfaAJvMm7ySTu5pnZSQkcMkNJ is finalized
Wait 1 seconds until block BLAUEZUEqJHmvu77hhkDVmQtqdBxdK5sB52zC6Z4Rpo5ayS6Tia is finalized
Wait 0 seconds until block BLU4kcfH1vDn4DaAARM7wSjqPR2Sr6qeu19kzJXEypLMJHNXfog is finalized
Wait 0 seconds until block BLRLUjgTFYAZsiwGRFcT1YWtm2rsKiN3sX1k2KEgiNcbRMsFV5v is finalized
Wait 1 seconds until block BM2YHMDqsDSUALKcy9upDobyqMPmiebePG5P4YUAjjVVoanYWRn is finalized
Wait 0 seconds until block BLiqpqhWjxytdVVGtkXnTEmcEiWvUxvYDFRjd74La3F76QbVaia is finalized
Wait 0 seconds until block BMbSvsr3kvDS3hahjBz1RbwQVgHcFrH95t3aVCXGGwzVtz4byPc is finalized
Wait 1 seconds until block BL4Rp3LewUtroQgkw87JqH2VXfcG1AEiWnZizQEZdNHamxinBtb is finalized
Wait 1 seconds until block BLjp5kbYgxoKGqm6bu2TTrXtDMnJ4ansAMChMfeNbkmeXf4vYkc is finalized
Wait 0 seconds until block BLSQcQJbnRo8XFWtinQvgSofn9GsMY7ee499eRmVauct64BirAt is finalized
Wait 1 seconds until block BMbCsHLgNSZH5kemgLjgEgCWkTxPNLhZztnxK99b73M9QMAztqw is finalized
Wait 0 seconds until block BLLPfk8SQq6kRzcfTnnFX58nPp4em8qG8wbe2TpSm5iakz2viv5 is finalized
Wait 0 seconds until block BKjVLbVFNtg72Aj28DHzEmAkEePr7bB3w24e1uUJT5VZaPwfb5Y is finalized
Wait 0 seconds until block BKycngZFbMK4ppWTnLYNv68m1c4shtbr1okX4wDc4zCsMMNVJyL is finalized
Wait 0 seconds until block BMRzaAUeFsZHzPdjvWoQ9fTTxQcSHAvjA3Vwfs8cwqMHp8XPcSq is finalized
Wait 0 seconds until block BKuGBG68UZ5wU6dGv5tipqbNRsTq7rzcKWFUPuh2V3iGU3WyKL1 is finalized
Wait 1 seconds until block BM4yUgSwjc7FbcKapmzhAMtQmgmtBLe9Qvyo3uGoxJxgWzzDaMK is finalized
Wait 0 seconds until block BLjQAYvABYGL1ZjHy6xtm74WUUyZHqufp7EoJj89NWdyYyG3z1F is finalized
Wait 0 seconds until block BLFt2mecXWeV5jJpyxehZbmEx1mZNMgFGHHqzcgzwfY2Z23K7cf is finalized
Wait 1 seconds until block BLbrj97nfhZFYhdYQMZ9ifsoJF7DzAAzdFbYFYQKQ7tNa8jxWPm is finalized
Wait 0 seconds until block BMFWzBQZwc2pgCxra5YyqTdQd2pzEZuBrutt7JK4Er6weT6A5VK is finalized
Wait 0 seconds until block BLUYbx5Fx4WsXY2mJd1Z9sDnZQFw2WKNPF4J3ZictCudR2FcrDp is finalized
Wait 1 seconds until block BLdqE7CBAJ5g6MsHgGBnG2ju4nr2TCTYadSvf2HdBwhadXiP44L is finalized
Wait 0 seconds until block BLWcejcRrKZSUcoEaypfeFowybmTHWTP9vbyYEnjS7U4G1CYzEr is finalized
Wait 0 seconds until block BMK46wMPuFiGCCSSDikyzfwzXJCiVZ23xAcKssnw1WDnZMrk2YT is finalized
Wait 1 seconds until block BKtTbp276C9JTES952oh4WgMqM9nQPgiRGfYH3v84CYMCktb9Ji is finalized
Wait 0 seconds until block BMXBQshx4RRrqX8yQ7AujM1e3ymS14Vk84avkavWr66fqLCvi8w is finalized
Wait 0 seconds until block BLnWZLMYwRgfrAoNMNa8dUV3Ewz1ebBxFxzgrPxkkDoJoTKRxTy is finalized
Wait 1 seconds until block BLiyQ6DJ23KCiJb5xi3RiWMYtQEQnYed43kxhDRCYszdKZ8zKjt is finalized
Wait 0 seconds until block BKq6WhV9LdEuKXxvkuGT3JiMNCnZ9ksx3ra47FxV9CmzC3htcWG is finalized
Wait 0 seconds until block BKyAQ7GERKfUXRrRw8beEU8keUAKcvWiyvp9xRvPLMBvrAu9P87 is finalized
Wait 1 seconds until block BLrz6kxviNZUbJEMfbMrqzesWMZGtti9DNstMc4bVhKj4CPwXgd is finalized
Wait 0 seconds until block BMeosoMQnhD4fFsG4VDWRcFDc2ipB6PJW4G7AhLceDZafEGu3Wa is finalized
Wait 0 seconds until block BMGEqZB1SESDGEV9PMaDYHSecGoscYg4oRFqMLELgDwab3rrXiA is finalized
Wait 1 seconds until block BMBBxF9un3JAhW2Ezwg3yCu3wjzkpb9ARrUDCf4ifZnubngG2CT is finalized
Wait 0 seconds until block BLAzxG38wyo3pdPkBw8Umf8SstdRuUzb4BK8TE1WweaRBU5BcQ8 is finalized
Wait 0 seconds until block BL1JD3ZiGxRj6Vieo5TVBmJx5ujPCjSFB9JPh3NLLP6bZq1bHiv is finalized
Wait 1 seconds until block BLoZd2tvoKuAHz85iQDiyunAtA3ThfkbHzzgP9unbnhLMz1ez2q is finalized
Wait 0 seconds until block BLdw5TZFtLovu1ZHBYV7PFYqkGZRytZhpJXUGKwx7ftfH5uS8Ez is finalized
Wait 0 seconds until block BLKsVTBv6nSa7h3zPa2WJwGpZwYnVM9WFzc6m5z6iGjaagBaKub is finalized
Wait 1 seconds until block BL4GWrBmFQ9aXMS4NX3J49WFraR7ptUgyY5SCgQNc3YiuUcqrkt is finalized
Wait 0 seconds until block BMJ3KsuC3iAhtzKvJNERhj8bbK6NNQuz2yopKevdaBTRC4THV1F is finalized
Wait 0 seconds until block BLMMEq5fK5rm4KdiYnis1Jir6hYrtoux8opMiPwbFwK1Vx8B53i is finalized
Wait 1 seconds until block BL6WddVC6k5Ahc2z6FwUN7Ro8tFJwABKmM1UCW3ZVQwMJq7GJWc is finalized
Wait 0 seconds until block BLbkxft9S5cBW2nw6kJkTH74hkTyYSSZCTWM4FzexN4vJ5psCmx is finalized
Wait 0 seconds until block BMToQ7ZmZ1DW25AShxzGHo2i9VeWbbcJiZciVh1p11R2LdZit2K is finalized
Wait 1 seconds until block BKqSo8KAjuLuiaVAdfQnf6UpvKqjcYGK4gVDCwErFAihriKC1Cm is finalized
Wait 0 seconds until block BLpn1Xu5o8RA7FmdNHFKVVunqb21FAK2BTmCTxUMWY8ZF4pZmGw is finalized
Wait 0 seconds until block BLuVQdU3T4hLvFTy7GNjZEqiysABkYmNZHidUXCYvpndRrri7hE is finalized
Wait 1 seconds until block BKjRNbvvQb1BbDD9S2uJHNxbe3EespDNmJ3hSkzpuXGJYGWMwqv is finalized
Wait 0 seconds until block BLbrc8NMdBJT4PFMzkEhZSyvZyd79FXTZC7N2cRqL22Ru9V67GB is finalized
Wait 0 seconds until block BLdo76YXaFEcu97tXGbgC7jLczK2moc2B5FjWbu7Y6vHQXYcxp7 is finalized
Wait 1 seconds until block BLFGX4LihFDcrarzcus3uR1kxkV8LYo8WY35jDGvp5qutqdkrfP is finalized
Wait 0 seconds until block BLUV3Ke5uYrqkC19e2uysh7frXLQtyCu6q29Q45iStixQCq1KFz is finalized
Wait 0 seconds until block BLmxC72ZrVJwwHDscknFsht6hQJSznxYHfMwuXeD6ahufRqALR6 is finalized
Wait 1 seconds until block BLV1DtaEdAxYLbkdNv55UYptaEmZSswmo3a2iMhwWSHEZApwt8j is finalized
Wait 0 seconds until block BLBSah37Y5pfVkjmQumgUUaarkKCfw2WnSeSnpi8hwUy2DmoQ4Y is finalized
Wait 0 seconds until block BKxPJ2XE6hQrTuP76oovN6BAzd6kMMVq4QS1y2ucK3qxjTytbwP is finalized
Wait 1 seconds until block BLwXDyBH968Ls1na23er5Fo24mXWi4ATFHUe7X7brwH8JC1euNT is finalized
Wait 0 seconds until block BLTyEoe6mB7hCp45hkWfqYserqMikJSiQnouYEQuhsTao2N4X1h is finalized
Wait 0 seconds until block BKmUWjhXQ3JvsvoCjrG5XHa6tVev55vJCkhn6TcFwvUp61xBQim is finalized
Wait 1 seconds until block BLU6eN1XE5meb8AHyfym31WX3a3wb8Js7nE57R3fE8oFvwnVNWn is finalized
Wait 0 seconds until block BL35kyTX6AstG1NgkDy4UTggoH3aDM7LqjHd8NZhHZWkfwgVVwH is finalized
Wait 0 seconds until block BMKKcWiSMMZEVQi6YfJGzfFeSK7k22ufvzFP1EeQNn5QZJAQyEF is finalized
Wait 1 seconds until block BMZ64apbavcV11PbZ6KyZ9vYdMnDcz2yGJqzbtQEPjT6WuFKh6s is finalized
Wait 0 seconds until block BKwQNxrvc561AxU8eAv7UZjHRqEwwhVD4v4AH82Ka9SdxsUG3e9 is finalized
Wait 0 seconds until block BLXh1L69ZJZhVv654Cq4C6WSJwriKwzyS8KKkryfJJdc1LLvGnK is finalized
Wait 1 seconds until block BMLGtCTPkP1WhJXvMECWBpv4QqgxKAKimQUQpGTUYEqrnLTXk24 is finalized
Wait 0 seconds until block BLjuqrVEgx4nYHbwGSmV949JFB5cTFbjJA6MKVXV2whPLFgK8NV is finalized
Wait 0 seconds until block BKjQsGtg9kM2c9ouXoLSsxNgMTtyWYfccC1qGzryikn19N8HvDR is finalized
Wait 1 seconds until block BLiTRVXvrpzQpkenzjjV6oK65HZzaQyPvSYfkw2eCbWwhef15mP is finalized
Wait 1 seconds until block BMFRzifhJbQCubTk92hpvJurbK41W6znS84LgoTXoXnRrF891XK is finalized
Wait 0 seconds until block BLscqFiDkpmHnqkr4WiRcKvVkS63H77esYyAqSHpNZpNJmRxpBz is finalized
Wait 1 seconds until block BLoucPSofeCg1BCv3nDE8GkwTY44ZkH7JUH5u4k3UMevxWvbJDv is finalized
Wait 1 seconds until block BM8cnBweG87Q718ESApP5bAbAxWmV13wucvSvMRUBwosyfvNeTn is finalized
Wait 1 seconds until block BMSoGorYX84cgs5k9WoSCqyiVXjFJMKWSKk9YGtA4Rqswe83KEi is finalized
Wait 1 seconds until block BMTtGW9uScMMJL1j197Wm7AUvvGFCGJKabY7nnjHah7kZVxNHih is finalized
Wait 0 seconds until block BMX6tf9j8NNskhQXKQmYJtaDJYwUdD8FFSSdCV6iU29bV5pb4eD is finalized
Wait 0 seconds until block BLbiZs85MG85JoRFhyJc6NXEG5SRkrk2bBUZYaUJywWvJS9QFRu is finalized
Wait 1 seconds until block BMBX7m7pbKYDPUx28ioARCk8WAA7mg8aQGcpng9QLhw2Tnk2VBZ is finalized
Wait 0 seconds until block BM8WtchCxSeRBuLuD7f8wgCjs37XtsSHXwZGPzP8dRcm9XDJQJb is finalized
Wait 0 seconds until block BM6eYf13iDwrc9eqaJBrXoWPD5RvC1cqfmdHi3tNqHv7d4xCTcU is finalized
Wait 1 seconds until block BLncQCEdcp2JcFBkQNVRpK4SWBU2fYXd7H1UbEYhnhkqzxpqbFa is finalized
Wait 1 seconds until block BMeKVPxuTYwY65HJ8jjwBSn4mpmjAS6xVjZcEKXPGsqLGquULwP is finalized
Wait 0 seconds until block BMQzk8jqoP7tZCMdHTxn6A9jd3wpazC7Bzs4BJe5Dn2m1nY6TQE is finalized
Wait 1 seconds until block BKij1oaKWhDTNDbpnfog5T1NAw5Uc3ree7Xn1khsbJst4mVeSTA is finalized
Wait 1 seconds until block BMND4piugF81tjjsNw5VSLVtqUAWUEBxwdTaN3q28gDei4Cn5EQ is finalized
Wait 0 seconds until block BLjg7e1B9oqzvL1k4QpfJ14UPsS8KxXepzwzrwVbcghRjYKGops is finalized
Wait 1 seconds until block BLD8i8eMh9Q6DURNZbFK1eMEXpX4JRt58QqTVUZ3AKBmngMFYu9 is finalized
Wait 0 seconds until block BMaZfa4k4kR8LX6wC2pA5QKNzfgfUxhyzTay4C6jsVoeXVzq5iZ is finalized
Wait 0 seconds until block BMb1RMFbLdayLmPuH6Yb2LCxHhbiXqeqPcExprNTfSXjUc7sLFh is finalized
Wait 1 seconds until block BKxUyvYhJqKLDKKsHNyPjkbzucokeZqi4H9CE9PxS49PCnxu8cY is finalized
Wait 0 seconds until block BM2bxDim5ap8EU6D7ZALUnbGkrieGFLPQjNXvMXZuhzSXZucQHc is finalized
Wait 0 seconds until block BMBNmYgHbdAh1T4xwUkq4VDWWz2AxTAmUZH5pe2TEC9MrYvPyqF is finalized
Wait 1 seconds until block BLEPjnQYkcoq6ZvUoDL1nnyQSSwFP6sK7d6BPDp1Xd6rdKMaQ25 is finalized
Wait 1 seconds until block BLPycG5Gc5FcfPUKyvTjYiNog4D4PVqjL3M1kj6tc36J2JA6SYc is finalized
Wait 1 seconds until block BM2CD2igb7tsufUSTc4MKGyW8tGCupmFxTuwtnrDbUk3pmH4YHC is finalized
Wait 1 seconds until block BLDHsz6PbFUZvRgNMPv9EtqHSpUM4VxcdbENfbupjQcm5hnPc2R is finalized
Wait 0 seconds until block BMYTPec4YuzmRGCLqemMEvRPdmmpKUBk88ZwFf2wRe4iHUQ5xXD is finalized
Wait 0 seconds until block BLJb9f5LPeQY47ZBKiL78Ss54WTg1k5RPrs1AdmCYU186FReLGG is finalized
Wait 1 seconds until block BLNsKG7NE9KfWc4BtCyLr4XjE4wBvC2Yd9YHn3BTbXCw9dVWNLg is finalized
Wait 0 seconds until block BLCbYdPW6ZhEWwcnBvCcXfLZieRWikzRTqbGZL5mPR5Y45WVhqR is finalized
Wait 0 seconds until block BKr27GpUUZwCkZ9bmJCuj8mc9qcLkoFEo7Y2CsqP8An7KfKu4ad is finalized
Wait 1 seconds until block BL5JZ9cEeRGtBE9oiKv3XBwzqHXfF2Eu4oFw33RSEQ36x8UWjRK is finalized
Wait 0 seconds until block BLkGaJ26A1dqPmye1pTtgLbvkwPb5HaUEPRFMjVVCGTRSmrapfg is finalized
Wait 0 seconds until block BLQ4kJPSCh6QV9jMeRf9GhgGcFihp3rne4eTpnAc32BJ56oTGZs is finalized
Wait 1 seconds until block BLRoyD8pZecuYC1HFyecvUj9JsYrms7hLTnnkPhNk6o99546KxX is finalized
Wait 0 seconds until block BLkZeCKSoSBTWheD2sqSb2BqTi31Qb9R3x56aMAuFivUkVpHUEo is finalized
Wait 0 seconds until block BLnFz6jSPreBVQM1jBr62M5BTELXSJiU89oVxxvjZbkDH8D5JU4 is finalized
Wait 1 seconds until block BL4GHW3esidY2qtvGYoZtepf4YvQJdmZ74rxGmDsupg8BkNqo81 is finalized
Wait 0 seconds until block BLmosqD3x75PASRYFQsttbhJKkHr4F9NS23qv1hPymZzjkXoq4Z is finalized
Wait 0 seconds until block BMXGuer4ycMMYouYYYjofDvZrraMeEoKmkh7hKX789f1ckgne8y is finalized
Wait 0 seconds until block BKjadfX2CDaN2vrBr85TRGYLeJsx55fLZ9bywq5TunhYKreegPK is finalized
Wait 0 seconds until block BLvrfBc18hSzJAaSsMqtYpG5pN6ffYCbJ4FJRoTvxJzRttGRLwW is finalized
Wait 0 seconds until block BMJfiaewbycqxjjwEeqm2DCZ8UEU1HA6NCwsF7c23pKBF2pehGs is finalized
Wait 1 seconds until block BKtmEJbwb4iam3cPmXMhB4tcJZJSCsmLMeaaCs5ACwFDrija1Q9 is finalized
Wait 0 seconds until block BLvwjz1dYYkhNe8YwGXM43pEn2MEZFcerFxy3kSvvt4mFLnh7sq is finalized
Wait 0 seconds until block BLFYN82j4z37g95iAvrtZdZVxFZcd3kJprETtXxECUjNJtCDdeh is finalized
Wait 1 seconds until block BMU8nqWuEuaA1o5fv6maNjPLyVs2zgjDSpqq4VFw7TTCoGBGuyU is finalized
Wait 1 seconds until block BLBUo3BpeikqZ7J1pKWXyRptq83XNtFrFnmEsGhfXNKfdMa9154 is finalized
Wait 0 seconds until block BKwrLXT12aLZvNNkGB3ykVGdCnnUk8o9tD74WwAfLD8PSixfva8 is finalized
Wait 1 seconds until block BLHUYrE3VgEmqhqLAuxijZXGSuCMSNSApMBXkcvgJMkZwzQ5sCf is finalized
Wait 0 seconds until block BLsGnFcD7cAGvX4Z7PaU8NQoQHPoay5WH13biKnYfnp786xKxPH is finalized
Wait 0 seconds until block BLG9PkASRbNnNbrJv5C6wFFHWfjU6vsVdFUchH5R7fTDfJkkxcr is finalized
Wait 1 seconds until block BLHjJ9xeNwCpHPzE12RTayBAYPrfa1vKYumTYCxwnXbDrZzvBnf is finalized
Wait 0 seconds until block BLKbbdwBepzr84SYJy8wSZ86c16HqF5BrocGNV5jEeij9qCbD76 is finalized
Wait 0 seconds until block BMGWPFY2aH6iDHtQQFYHc4ZR1qevdzHWE3HWAMtkf2Hsn1ygPzK is finalized
Wait 1 seconds until block BLMYyEvMobTqtJepqHcg8SxDztHYkXGATN9xyc78VZW9eLJYcgj is finalized
Wait 1 seconds until block BLCWCoiNUz4sgRDPKLss2ujb2xgKy2TGNDjjqrT3iTASQShYoHV is finalized
Wait 1 seconds until block BMci6nXqA7Z2xHrtMjXwVgeebfcPoYij2Zjfezxken3f8VBfM69 is finalized
Wait 1 seconds until block BLZwuJ3efJ1DEG3qWXLTLMUJhQtxtVZfCLrEvY2FUYHyLbrAVeN is finalized
Wait 1 seconds until block BLANYGNcs3khjhfJT1SQ5x1TzbE1ewPrdExDgQqiY3xtRbNrbaX is finalized
Wait 0 seconds until block BKuMHCGFCcENKvCSLCta5Xegcv8pRQb9wRmHDsQ9VLWyraCV4UV is finalized
Wait 1 seconds until block BLTGZxnKMDJh7TXgnjmz34a47bAoiWbF8p3r5NcUNZnhieYjBzK is finalized
Wait 1 seconds until block BLVWyjLAkkVzeMNg6tg6tVNDgvbigio8J2ygVmU5V1qjnh8FmJW is finalized
Wait 1 seconds until block BLn7e6rNV729Yb2PbL7CaN6Vr4txhjgNueCaSShP99KAuzhCwAv is finalized
Wait 1 seconds until block BLPVNKhRsPdZqQfe3junZ1gjjkBSiXmANTDNxr4Z6kKngDejPRo is finalized
Wait 0 seconds until block BLFYVAdV1XULZd1XSvTfeSRxaNUJNMUtgidMZimk2sit4VMQNv3 is finalized
Wait 0 seconds until block BKtZMZEvjjqKr6uZ9oTPZmGpT9WPuoEKRzpnFUNPiJiUNzHu5Ar is finalized
Wait 1 seconds until block BLpmEDrAWtBioxoqn9pDJByQpCbruAGET2VoYgDvGA5EAwRkNbQ is finalized
Wait 0 seconds until block BM3zsxrWrnL3osc6UrYWsAKvkXdqWrW3iGxz2kCZaAspHUD42Rm is finalized
Wait 0 seconds until block BM2zpqBctwZdvHaxoJVV7yhAcd1nMXs2Z5vGtXv1MnZpkK2ijuZ is finalized
Wait 1 seconds until block BMdzcqAqhtrW1N44jV5BAqX7JGVHvsRS834nvj64LEPE31G9o18 is finalized
Wait 1 seconds until block BLEwpGeYMXtccJFCGQFgFiuBSe1Y4exTiJ17jnBfCdtoWZJTSXT is finalized
Wait 0 seconds until block BLLwNoiyngDhVqHK9N5H9ifhH6vXQSmRHQBfToYBRVmZrERaJC9 is finalized
Wait 1 seconds until block BLAQU7EvHqtvAE7BQa21CMGxmWh37tTo1vrfCLdbiQ9t89RPsWv is finalized
Wait 1 seconds until block BLignE8WVLRJaUfEHGaC4imQA5A8Ky9XyPnNL7gji9xJAQaig5T is finalized
Wait 0 seconds until block BM374LGA7fXigrcmcDqbBe6z4kCWRkJwvT3RigdSTfsAvukVFDk is finalized
Wait 1 seconds until block BL8jYvYrbWm2gwNN1tUTnqUdtPw73dHvX8Dq4FVpR2Uk3yTYt1d is finalized
Wait 1 seconds until block BMBhapwdMLx3Sgd1Fxwm8q9NafijELcmCNYrwRrfFKTdU5d8PKz is finalized
Wait 0 seconds until block BKkFs6y6XqMYDtdS2iZgVDgYpS3njwTat9eKenWMKJPdbtGGDSh is finalized
Wait 1 seconds until block BLwsAoHQN5zFQFndb4jnm3x2TGyZhL2ViBisfGMconC6DDWixJ9 is finalized
Wait 0 seconds until block BLYBDRUME768vkbeoqBS9CmKg8v3KNHJdk97so8GeYTVXQ9Lyar is finalized
Wait 0 seconds until block BLJN9t31TdTU2VYFfqCGbCWcdYE4a7UJwpBmJY8u5GWZqA522ZE is finalized
Wait 1 seconds until block BL1axtchm7TnQS3BipdbAxkmjHLkHBEP2swCM5VqKgVJay7ryHP is finalized
Wait 0 seconds until block BLHgvzMPojgF1HaZ6PZCbwYQtDdHS95dLAe6PksytsY5monJ7Z7 is finalized
Wait 0 seconds until block BLyzUwyctBvsgBa7RFcLUuMqgshiRo1C5awTnGqU1M9DHtQXVbD is finalized
Wait 1 seconds until block BLNzZhD9CacfMx7kptNH3hSkkJCAwZY5XMYVL4onwa6YtfjWAqw is finalized
Wait 0 seconds until block BLh7sGujgfrbj67rKJS3pe2LJekS3AFfZoRZgJBJHUuCFEiNgr8 is finalized
Wait 0 seconds until block BLH4cwq2B1CESapr5am7x59q1wwqZTfQJgjhUc6YFdSArm8C49L is finalized
Wait 1 seconds until block BM5YGrgbAzzw9zRccc5Urm9hGXC8zyTmPyoSCkiEum1xQGD6bRw is finalized
Wait 0 seconds until block BLE8SQBa6LCe6SPoiGZDp6BEyqWQvHNoFzFk3fQyL7uMFkmRzZB is finalized
Wait 0 seconds until block BM5ia2okqHZ52L3rsYatVHvrvUHwuHhrGeku6u6MxH11Rppy9WZ is finalized
Wait 1 seconds until block BKzGgMSvjLHXkuxDBvcToR67DWqMDnKMZ6MSHiYMA6cNUxpbqN2 is finalized
Wait 0 seconds until block BMWTGuRUDm9hbZfGyHu12aUih58qjQESZMEyCu7ZUQxDkhWHFXB is finalized
Wait 0 seconds until block BKm5HHtjgZHJ153s6P2GrtSqwk8qW7Ct8ZDAmTBcV9bfcXn5reu is finalized
Wait 1 seconds until block BM8QPDDwwWVr45rcPKZWtBB3SAnytRizkeqpKmPzrTk8HbtHAgm is finalized
Wait 0 seconds until block BLMTRkx6dWRDoShVSitwHefPopx8ioURLZUW1VB8fSNjKapSCxb is finalized
Wait 0 seconds until block BMRAhvbEqxHCQbFG4jqmzWRV3t12M73kUmcaWj8gNw9Dvzo58TF is finalized
Wait 1 seconds until block BLu1tUKTydLNwX7YF6LtLvx7xL7uaXvnppyp3WBcywtV5vmzsxz is finalized
Wait 0 seconds until block BKt8frkrAUmkXWvpWJALqpN5VQcd5qTeoMMFYjLH5evXWGhJSGn is finalized
Wait 0 seconds until block BMJaNLck2PCJgL34XiGGdaNKxquaW1xFw7NvN9CFCi6QjJooU7H is finalized
Wait 1 seconds until block BKv3d9kE6hHp5WGvPWTZEMZnVNg6ojczKwzk7D82Psf94jpJhLj is finalized
Wait 0 seconds until block BLzsRwisbCJPPjytJRk1poD9SNo2wVkA4NiGUV9eEyXQD8qAtdQ is finalized
Wait 0 seconds until block BKqzAcT1MRYnrKcGFBNNpjuk2sjdV6xhwbewRd2ZdLRVW3hXoKh is finalized
Wait 1 seconds until block BLjg5cvb33UHG6kCggrPyKZMijjeraxDQJpwC2D2PNvzUrmga19 is finalized
Wait 0 seconds until block BLcHZwB33MYU3YaDMM35n5Yx8Soc4KxAt7y5LgHVLtL6mh2Hq6t is finalized
Wait 0 seconds until block BLtWsmkDnhZ7pSi2HHh7QrSgGpCRuUNkvGMr9EMJJDMtkuAWfa5 is finalized
Wait 1 seconds until block BLbXnY74kEdeKCQm2QL5dHRtwyp8ifrGpvKRLzcYzpjszZPiRE2 is finalized
Wait 0 seconds until block BL6uaXmLiQNWMXzLvrdqY8K5TZXD4bcUG152sYu52okYcvZPwzU is finalized
Wait 0 seconds until block BLJmAtEfaqhbj7QKJgo4p5s8Z3NWrb7dvxPvgri5Ft4c95Cp8iD is finalized
Wait 1 seconds until block BMMxwWPrNAdhdrEwnDD9TDkxQY8vsshi9n7VJYGa6Qk4PAGn5YQ is finalized
Wait 0 seconds until block BME3rTCBCCMwynKwZbSGAMxZ2G2V8RKpYfxLbt17fW87CyQ3eNA is finalized
Wait 0 seconds until block BLGg2UG1ZFq5KWw81yTMt4Q1KPsWpzC6WEdXfSTRGLe3B7petPf is finalized
Wait 1 seconds until block BLNEC8EBBLj16wUgGnDPL9cGhrD7hDtx3vt4U2FbioUUmydoNnf is finalized
Wait 0 seconds until block BLZdpSnBx7rSmBi23152JNcMso9VXBStnk84jgwxC6cJYwa5RGg is finalized
Wait 0 seconds until block BLyH475XNYg2GEc1dDrL4iY5jUaHy6vmCQ14EMDiyEJ4chPnKNQ is finalized
Wait 1 seconds until block BMWeqfRwqxvPiqDVu7TakKMsAXKqoDQidbB5ifxjsxHQxrAozW9 is finalized
Wait 0 seconds until block BKtQGsDyL8HHbuwP74euwMLUHfUdcVEBh9fWLrcsSWsmCpMMs34 is finalized
Wait 0 seconds until block BMDhymB4ALVhrFzQvz7KCL8PaXmuNjrkaYvUP4YSFrR6dueaATk is finalized
Wait 1 seconds until block BLSecxjrBnt9BDrfNnVQn6Wuxm9mdn7FWG7dH8dFr4BNMTayvFS is finalized
Wait 0 seconds until block BMKsbJmyzB4jR1CkfCf9bpCBdtU8o7T5nFyg74J4r818yVCKcrR is finalized
Wait 0 seconds until block BLqLR3ZwoYcECUviLQAEg6xrPwtwN9nnrrBibWAwf4c8tNFERC5 is finalized
Wait 1 seconds until block BMG3fkJggvJBrzbTCNbNGMTmXTDNihW6ik4YZtqKohaWyWsYGpw is finalized
Wait 1 seconds until block BLdHgKseFTZiGnR13gwomkkGkekto1cDaiCCkAF5ZLDUEqMH4qe is finalized
Wait 1 seconds until block BLhPCttFp6YSLFe782yLXrZi2SmBrutrPtd8WTLZzn24LQTJqN2 is finalized
Wait 0 seconds until block BL5HVdUJ5jbXdRRp8WgBSnPu6NRPWR6MCUvDLkAJYkh8dvBuz3i is finalized
Wait 1 seconds until block BL7KTWL9KnAdaMijUkWXk4h8rJZLj7uiQgkidDNAtbWdaD42kxe is finalized
Wait 0 seconds until block BMA8B8P4rRCoJ5TiC4cLYopYr25rv7rJBtRd2YAJnvWajMvzdsV is finalized
Wait 1 seconds until block BLQFqLwPKjMgQWULBccRaEFFSA1aPuCF72ChtHt96V7gNFMqu2j is finalized
Wait 0 seconds until block BLNNsAUyRnyLwJ4GxdAwF3BkBuWgSQnSKmnFcP7NzKg45hrwKbB is finalized
Wait 0 seconds until block BLoK1Ae8T2DUZayLFdnDok7TWXiWZ58rEL8pKZTpSEghGsBFMn4 is finalized
Wait 1 seconds until block BLFXVMTsLgh2YJZByeXCZRzy1CJoNqFE8PF4w6XwAJRzVYUaM2X is finalized
Wait 0 seconds until block BMNkLR4V5EE6rCsBkcbXh4e174q8qR3FELeHGiNq2xaFDywiyQf is finalized
Wait 0 seconds until block BLG6oZ2n2BrCvqMWbw3v3nnodYdP816CZoFS6AqzLNKTXqrBFvS is finalized
Wait 1 seconds until block BKj4c3TqfvgG4wiwcbpWmMLdYHPAB2oQTihEerFcjjrgCD22Drb is finalized
Wait 1 seconds until block BKijRyvH2KsJDx1A36ZG8NxB7MeKQypQD7Fs3vzJWpEgxFnFUS7 is finalized
Wait 0 seconds until block BKnAK5z9SvYrArhb3sqKDitfWCLXi22MpeVNxxd87pfRWzhAdDE is finalized
Wait 1 seconds until block BM5z2nyX3hjUhETVXXWGJAx3Jx2Jy7jQkTh2Ni9r4sp8Kdtufwc is finalized
Wait 0 seconds until block BLdjysjsHqdu4ZMk4nc8RXJcLnvhSkaEAdGQn6a6wbBK4j6QSVh is finalized
Wait 0 seconds until block BLMsc4GKda81ioq9WWu2eQhwYU348D7CgvwNSN2JsckHqpCqRmw is finalized
Wait 1 seconds until block BMR3y1x2gjTqwgTjb9LTj4Uy5aKZJerQopphAPvSC6qu8qdEuvH is finalized
Wait 1 seconds until block BM3VDiEsnJSNsSzBXAUwAPfhMBKrEX6MVkkQqp2fUPhtVfBNyd1 is finalized
Wait 1 seconds until block BKvBVZ66iB9jBQvturFfVTvs1ChuTP4bfTyZExKyaTitLtBM96m is finalized
Wait 1 seconds until block BMdprkcyYpMrJz5GquFeqzRMqBGFKnjepn6fg44tVvZNRmp9GDn is finalized
Wait 1 seconds until block BLjWBnxyVtsw5VU5Wt2k9oACgZVVxq6dTLxvFCNsmpWqEyyRATo is finalized
Wait 0 seconds until block BLMdAv2zMCNaAQzViE5YaS5rjNkgKmQYYY78o3iKiZna7sDd7Vn is finalized
Wait 1 seconds until block BLMUvjofizxLESuwH8V8HejdHhvnJupt2SYNBbdhAgrfwRfKSJu is finalized
Wait 0 seconds until block BLfeKVYCKNxaKjLzKjku1Jvrps58NMFdd8Ky49Mv5phU7imdwR3 is finalized
Wait 0 seconds until block BKqaMSfwxppCL87TTzFprxz2hSZuoZikghC8u6xhuAFFpejK5bz is finalized
Wait 1 seconds until block BM5a9kAoDAF4oFXcVhpdzdAyH3NBhaA7BLoXjWBtQ1UPr6FqNe1 is finalized
Wait 0 seconds until block BMSH3tURSTEawpVTkCzCK2Ps4AvUWY5cBct4CaPwNRR48NRgqrv is finalized
Wait 0 seconds until block BMT8d1jsEKWjQFjhSzop9T8W8CM9qKUXAUERGDwDYD5ryRv9W8F is finalized
Wait 1 seconds until block BLf8PfNFKRHzrVXdWxGpSqBLuHMp8gxJ3FocEeCmGU8RxsvpmmB is finalized
Wait 0 seconds until block BLox5B7U8wxwwi4MJWUt7KHqpttqtcBxzkBLyFNxLRGsqzm5bvQ is finalized
Wait 0 seconds until block BMLbSKibdmy47yycR5RxYyS56QRv2n12CSiheM1btWydPa9e8n3 is finalized
Wait 1 seconds until block BMAbLdsATCdSnoii6DQTUg6oL9nnjmsWsVaK7XtJJP3x4rm4DyF is finalized
Wait 0 seconds until block BLjU7bSpworgSig2UUKqErzBTbPUi1hLz1VjrM6CyrYAaHArdJU is finalized
Wait 1 seconds until block BKtf53QSghJgHYboVvxHc2njan6hd1DHfMm1mXZEaFYVKfJYYhS is finalized
Wait 1 seconds until block BLRuAdKBNMdep9vvoerDkKZ5hWAXCcmZ8aDfFu1sG8FWQp83Q4J is finalized
Wait 0 seconds until block BLmgDiALVPMbFpKi6rUpUE2Gp1aXdv8G3NoT3crHHcD5nqdJY3y is finalized
Wait 0 seconds until block BLiVVCbAAeLsqqVNZePBxjsDmypVCFttrKwwFgMuswmkThS9745 is finalized
Wait 1 seconds until block BKsVdCE9zjS6UWzEefXAcCdNY1o8UkQdvH369dUfBnfH4QTh8iY is finalized
Wait 0 seconds until block BM5fQQePDECKpBtu4ChC66pBf9eJfiiVrbbZEi6wkcNbNVL6PxT is finalized
Wait 0 seconds until block BMTwXTrdpqkEAAaAh3BEs3sRj84ZCZnrpNk6dSfmquXqwBBX7be is finalized
Wait 1 seconds until block BM8cGKHbBfiXWZgKYPBSeVss35QFYYLgVihtAVknTyoc7BP3oqK is finalized
Wait 0 seconds until block BMJkXG3gVLX8M7qM7ocRd21DBp9CyWboixK6ykM7HkEgxvtaC9Z is finalized
Wait 0 seconds until block BMS81hjHUXJi8U8NpveGaHZecDJUUGNRN4qZP7fd6Gv9hwQL2qe is finalized
Wait 1 seconds until block BLmaM7Mf4RWJEV1L1F59HofSSqivbYk6eURZP524LuhfNtv24Jq is finalized
Wait 0 seconds until block BLSk88kooBqW68pzam7ZZi6Y79X482Nj7baQjaSPgGf3yN1aju8 is finalized
Wait 1 seconds until block BLBdLBVULUssDorF7GKwwqNZsm2MxAGGpY6JBh8FkXyyJpTxrtv is finalized
Wait 0 seconds until block BLgVAd4n6ctJP9CJpjSYWNh1Rv3NdHmFhjhugqNvFd6YA9mehZs is finalized
Wait 1 seconds until block BKkuKgJk8iDi9xaC4XJ4hZDMUUJVaaGQ3HWUCErTYyUe7iQhKyH is finalized
Wait 0 seconds until block BLc5dn883Zkj83ovDxiSrp84MGP5Zrz4tHBJmouqEuJPrsc8GtV is finalized
Wait 1 seconds until block BLicCwrF2A5w7JafiDd6tTD2MXCajwGpgHXDQmGQZgfSwo3TX8n is finalized
Wait 0 seconds until block BKtaWs5yEw2HaUJ5XGfSdMqaqQkW79CRFX4nS4W69kMg3Hf8ds5 is finalized
Wait 0 seconds until block BMNN1rd5aG72TS2FVWnt16THUZqrZJcuEkWNVW1sQP1LS5R66oe is finalized
Wait 1 seconds until block BMRY6Wk4gMQttZMoU6t7rrWyXF1LKcmC6928ffwqUtSLpVjz7PF is finalized
Wait 0 seconds until block BLvgn9ET83haeuxTe29y9Aj3KuyuyShrxkGMzvuH6sDKNXjUqQb is finalized
Wait 0 seconds until block BKtzisfweZhdqeWxJ6MeQQCdGX2saSn4pbHQMY7Foo8s6bGgfJq is finalized
Wait 1 seconds until block BKr57XPDKgPGoPNNN4gAaPwxC8amZz9NuJDfQsZqBG3f5456xYn is finalized
Wait 0 seconds until block BM37wvCrEJ3edbr86JxFBT7HmCFzcfjgCJKR2vLiTq98JRLzfWf is finalized
Wait 0 seconds until block BLAyzkKKGCEcWL367E32Nkz58KGy3dJ9txiuPSakNzJsNtNA8E7 is finalized
Wait 1 seconds until block BLEVmgAicJMx3iPFy1vkUzbYRDxNobVRKK8JnyDizxKPnYiWk9S is finalized
Wait 0 seconds until block BMBE9JBaDdtYLyN8ZXFMbzppiaed6NR1AgxEMjZyEXGr9PmGmKb is finalized
Wait 0 seconds until block BLuQkB8X51ARAgdZwcrzeGKYchfy91cBj9qqFztvt3veNtKC47j is finalized
Wait 1 seconds until block BLKm1FLWtftVfnjRTMyBndi8crxnqY39hFni5fHkxLFKvN3z9K6 is finalized
Wait 1 seconds until block BL4Dw6W5FdHFBGvcgHomdrfuQRkbMmELRVhmsrcyiuEXFXht6qA is finalized
Wait 0 seconds until block BL4Gt5KxKRFG3MAWVPq1Gq6PcERWLhbLH8FGJvCePhnaTWAcNiX is finalized
Wait 0 seconds until block BLZconpf3pid4sq7HuArNwVKjh1iNfzEChZVE6nF95EBEe5mz53 is finalized
Wait 0 seconds until block BLk4fAhjhLjuhpZzUGJMqL5NyWcLHmKWKjoDkefSdKhtN1MqaPc is finalized
Wait 0 seconds until block BMPTDfPXJR6zeRwEfaLqGKPU1yRxTEHomHh7B4dstfP6fETjJFY is finalized
Wait 1 seconds until block BMTieQjbJAhdPghMjUrTGKY1fM7tPCi4DQNSyU4xCt6ACxcWdks is finalized
Wait 1 seconds until block BMcAuu2xmw3KCzSHqeM4LJNGUyzbEw7nnJPqjXUceYVwbyQUtLg is finalized
Wait 0 seconds until block BMCnds8nDUF2bgeBGo4NCS9kGzxSHDSiopVKFn3h7qobDuf3p4f is finalized
Wait 1 seconds until block BLNEXVMcCtWv2iNFbA6mGSgmsYPLEumT1Co6frTQSPmYtJ6ACCi is finalized
Wait 1 seconds until block BL9tDrkaLX8kg2EX4v4Z4kpy6XZaDWDjskE76CzAMbrZwyMhkVJ is finalized
Wait 0 seconds until block BMC99qoFEFHcQXZc7TuSxXhNbjWx1gexxKYkJAyDa8BchJbxU4v is finalized
Wait 0 seconds until block BLrZ7GJ33b1bKxnDs8WwRj6ro7rneNihDHKkdZGESXm5khxq4EE is finalized
Wait 1 seconds until block BMeVKJxLF3AkyjcHESo6woG5RQCbUjcsLwRWTJz8c9EuF8jCdWn is finalized
Wait 1 seconds until block BKxDvcBthaK5AMQW7wNxUgAdLFVTxicmtfR1gTcEapbJhhtCsGe is finalized
Wait 1 seconds until block BLJ1EUVkq55B9q8JMYEDu4bt8wQHD7Hs6CVbhqoYCQB76vEyS6A is finalized
Wait 1 seconds until block BMLiZF9GPpkkTZtTwXjqNHMczhSdVU1JHGiwDnFKraaT6TZczbf is finalized
Wait 0 seconds until block BMMzGmADjBmr9LB7qaHAzm7G6ZyW9Afqdd1QWSo5KXuYTiE1ZHM is finalized
Wait 1 seconds until block BMP52sRRcXGwmG6zpr6BKPEYMqtFVT2M399LH5yXYjTo7ss5hCs is finalized
Wait 0 seconds until block BLfg78p1R3UJ3EZtkZQyoi4VhnwdGvKLSqkajH2U7uBoNwJmjWJ is finalized
Wait 0 seconds until block BLvcK6q5EgGQc9dHxSeebNVE7iMzLFgrnMeFFmVhFh5Jqiqncgm is finalized
Wait 1 seconds until block BLCrGoVR3feVjQ6pJv3pEKWEGBV3qedzy2fRUwycrzd6ova4Kzi is finalized
Wait 0 seconds until block BLBZfDw2MSM4fj5yP1f5ZhhSCGete4J52BDQmx4oHnJihPAHWda is finalized
Wait 0 seconds until block BKqC1X9Rg2RoHHLxoHwHXiL1P1UCAWJhPYtLA6eEdFhzyLj4KBJ is finalized
Wait 1 seconds until block BLfBXMnBXcuN93SsjjSWkuEH6B7Yw78Uv3XAtyJYNkJvKUh1BBr is finalized
Wait 0 seconds until block BL7r1YfCEQWZYms1eH6J643Ryw71qYHBYavpXd8o6TSeo2mn9rN is finalized
Wait 0 seconds until block BL44ftCUYios8rjBLeTFDvoU5mKCv263MK3LCyEsetSwpFgzJG9 is finalized
Wait 1 seconds until block BMN6YnzxWCZUWGeWgMCbpRu2mDaYZdQnTHirRQU6YrgcRJunPyc is finalized
Wait 0 seconds until block BLMsw16adTnDM1KpdfLmWumJgLFXggFfJwZvsrNynofzxBeeYXZ is finalized
Wait 0 seconds until block BMRz7gRN5h3cvrQjL8sgEzE6QiwgmeW3xaos8Fk2UzniULLQbDZ is finalized
Wait 1 seconds until block BL6NYb5TKJvNBWg5YvLmKgkFDwa3HArxmgSCkaepJX66wiN9mbE is finalized
Wait 1 seconds until block BLBUCQEX83hDUZQ5eQpvU8xJrFT2GsUK8qNEU8r2paPapS7ChxF is finalized
Wait 0 seconds until block BMFBXnw5dEApsQns5BVE5qPTHNqTa4KJ6iCC84CURxJBJqnFjPu is finalized
Wait 1 seconds until block BMWCP7GSksQFVFo691PZjAhpQZcw3GCrwawciAk1Dfkn6NLfn47 is finalized
Wait 0 seconds until block BLLeMkz3c7cbxdeFPJo9uP8KAxDwC4rkXaBAK8cfYMVCZ3PHaHc is finalized
Wait 0 seconds until block BKqJJ2Draos1XXqjG62WowD9E6QH557eQNpBdPYFWvohFuCbiq5 is finalized
Wait 1 seconds until block BKp4ueo7hRbaAmEPEv95iy3AxKmCTtM5GY3yq9NDiHqHiv9JUGP is finalized
Wait 0 seconds until block BL9KhGmb69BX2vrFZgnc1DUM5Fp2rZdNrK4GXVpDnrvRMTDBw1r is finalized
Wait 0 seconds until block BLTdt7kTtvfKs9JJXM6NRKsL5BDurWduizEvFdxy7SYv4cvNLNi is finalized
Wait 1 seconds until block BMCMakBamcAkpErf2VzyVAZvGEnwRugEJzaS8P2fvWpgrt3of3u is finalized
Wait 0 seconds until block BLngtYpVfTxD7vZWFa12eY457eGtoKGn2JVEputvkJtjw1xYCP9 is finalized
Wait 0 seconds until block BL6mqAU1FQRqXjGZcaNYrgR7EUy4wobPvYwsTPZxb7TrWkkLpgx is finalized
Wait 1 seconds until block BL8899Nj4GDn4x1VVnJSTaAnqBrGEySx911kFUMxppbmDu56w75 is finalized
Wait 0 seconds until block BKq4bzKDC2fdXwN6nfhd3mmBVRC4TPmc4VyxnGNETZbGGy7cHw9 is finalized
Wait 0 seconds until block BLwHtcBbHF2J95EjWQeBcZRbCEFev6H98QhGUkpYU3SdVZWpHBj is finalized
Wait 1 seconds until block BLZxUJYxe2tp74AdT8pVVfBKFt3fenjS1N3nRB44EWd89CeB6Gq is finalized
Wait 0 seconds until block BL3tBXrRFBn2sXg4w9WSQ8vYeRAwmQZ2Ht4zzGtJMhL8FMZEnd7 is finalized
Wait 0 seconds until block BLWAZSvqdaGnXG12nRv6RJ1eMp1f87afyrcXiFippc17nEXrdp5 is finalized
Wait 1 seconds until block BMAXdqBytYRpKFTE3mACFJXXMsCzQrb99Be1DrtQS3o9vZSA8ax is finalized
Wait 1 seconds until block BLBfjSJKQWSmAB7nSghRa9yNjgfVfUjwzaCRbKUAqxHdxp7kYyU is finalized
Wait 0 seconds until block BM4dJtTgVWiwTYyHvLYhmugiLqYNYuivwbm6JfNiAB1tv5SczN2 is finalized
Wait 0 seconds until block BLt23hUed4YKzEoeoApR4c6YbnPCAKXcACU8NyxdcoeXDnHZQxT is finalized
Wait 1 seconds until block BLKZhAhK68b2H41W69Hbe7UK3uiXoerBb7oqy4haEbYpYvVupsd is finalized
Wait 0 seconds until block BMWyoeRL62v4okVafQ7NqLtmSYsVURrDRUbSe39vwUHVXgJ61S4 is finalized
Wait 1 seconds until block BKoVdKKYctaQN87TuWrSN4eubCHRokCxgxbo7cAv3khL8eXx1JB is finalized
Wait 1 seconds until block BMWtY1dV8jxXRm4ataH8QFgKxQ3EKDWJL7UNQsQQuNvbCPhAjGU is finalized
Wait 0 seconds until block BLSqY4JjuYm65QYeRBPYDRa5FptmaURRyAfGDmTKsUK6Uvp8uGd is finalized
Wait 1 seconds until block BLJpu5CTrYJdFYXA5bbb13WGZ5gzLGS2YM1Qomh2wVWLj6W99rq is finalized
Wait 0 seconds until block BKuoanmVTvUH345HyDzqgCzxV4QpnqXxcoRr21Uut5bcZd7poN7 is finalized
Wait 0 seconds until block BLH221uZnWH4QdZG7g6yyMcBitEBvGmavV3MXN4QuwJsBYooM6Q is finalized
Wait 1 seconds until block BM2BNjy9jBJ6ZA9hHqRLeKqvcjdCq9AFNapV7zN1h7BLrUcLq2i is finalized
Wait 1 seconds until block BMH2ZuQ8LwXV49xi9pVLkZfwB5rhVrZNzN1xHsUT6tHxiCQCFeN is finalized
Wait 0 seconds until block BMMH6SuoUBgYZ8PciXJ7FXguhASDhxPxSYzAhhn85veohwDHAnc is finalized
Wait 1 seconds until block BLuTzNyqKpJB21rDULBHABoXZYRi1dAeDfwpHKv5khRJZj5Drki is finalized
Wait 0 seconds until block BLStcUvxPCxTAj1kTFJih8KKnKFonYcDk2ssfCoDqXBNtS9Z8pf is finalized
Wait 0 seconds until block BMRxPF4SbCJdvBt5wGnSVLPrhqRMD8C6rTitNb7QcmPaHVz99zL is finalized
Wait 1 seconds until block BLLPTRJnKi11R4DTc3brhDWUcTfL3eZKexJVjmFfthgVD2DYZwg is finalized
Wait 1 seconds until block BLtjoxhsW4XYG5Yd8gqvhAxY4bsnrvZLZGeWNwTJQGjKjgvv4dR is finalized
Wait 0 seconds until block BLy7RCYnFyWEBD3iJq6mg3J3BQk8KbnefS5PVeiPnGNqxoiFjfg is finalized
Wait 1 seconds until block BMX4ciqkQSeZLfeRZhDt8nu5PqLt3ivAbQjQ46CqQKrY2LveLD5 is finalized
Wait 0 seconds until block BM1MCx2chW2JqHHPmsfQX5Ro7CGTcbo5vvhDnueCUV9G6LQ2HK5 is finalized
Wait 0 seconds until block BLSq2iaWQC1RHz5cFZ2gq53CwAQdUcC4X63KUSxkensT3CHJT5v is finalized
Wait 1 seconds until block BMB3sf323JerDYBB3W5Ce3grURMN6Ei7oa4xvc2KuAey1QbkATF is finalized
Wait 1 seconds until block BLvoR1NTiaSmBYvDX43wmjqQr9SVdM1acTHESmqhw15FHvZFk3p is finalized
Wait 0 seconds until block BL6RZwzNePTx3ztgGJDrqeYvaRSxWAWja9DzDF8mA97BMmWTUAP is finalized
Wait 0 seconds until block BMRD798g2NkLJjfgwjBS7wnreiKW2Yi7jRLZgWPDM5DLuCbpown is finalized
Wait 1 seconds until block BM9JH2PnrovTTytHTBWxotgvy8UJXwx466pqdx3fV2wJpjzAKFe is finalized
Wait 0 seconds until block BMEJq9uXKPtjD7EK9a9Q7x3TXc8tkmMUqvjeLuY7mnXh52W4nBL is finalized
Wait 1 seconds until block BLzpgWT4BWEm1mb3tegBhy4nNKerG5WUKPuNgFT1XUGxbvU6K9k is finalized
Wait 1 seconds until block BLWqLZWHnuTay7eUbPqKMtf2iB7WEY5kkfWCtmUzYFSu887ySdm is finalized
Wait 0 seconds until block BLexkgAxxQ1Xs4fGsMkeHebYuuwVtQ1zJeSVoT8YEJyNh1bFsZg is finalized
Wait 1 seconds until block BMXak2aGJjqBbL9qMGpsQy91qQhUmETGetskQMzdp7ZSgjdP546 is finalized
Wait 0 seconds until block BM6N8KtVvarA7JvhEBMjCAGkPP6TrfZxf1ZnvAGjK68AFcz6sfr is finalized
Wait 0 seconds until block BLPkyMg5y67xjL8nXbAomfqduK2GCPFrNenRQ9ywrmKYDY789Wa is finalized
Wait 1 seconds until block BM8r1mqsNECuzvBGGrnkk79wBMDjVESyS1xeBQ7ikm2Eiteh5pj is finalized
Wait 0 seconds until block BKnJot2pcDNp8UiokpAxeLpfwX74h4M47XDgNnMExhjzs5bABrH is finalized
Wait 0 seconds until block BMY6q8ijAvwrLqFmNFw1RB4iUyqCBNLS6cAa4h1MUxXbRbiKnWN is finalized
Wait 1 seconds until block BLDjLwSZK4xbU3z8UJfeNgVNVorS5t85Pst2zzUA7EVmtYnvN2M is finalized
Wait 0 seconds until block BLnodZpsziYGztSUVBMD3HRM97XjAvbmoTXqd3sHCTSG9xrMASK is finalized
Wait 0 seconds until block BMcGVQWtobXtwMD1qevEzTJwneU7KLz7VFm66rAnyBMfkax2PGm is finalized
Wait 1 seconds until block BLadhPJeYTLYesYABJ6msD752b4yLDCXcmTUDYQFoSomAGKz9tx is finalized
Wait 0 seconds until block BMQ1sf4WmtjNQnzt2WG3PxxCknfMj4SnkjUzd1mygrkB9TkTWZq is finalized
Wait 0 seconds until block BM5FN4UyRwqZbokTzyZnTJBg1dkcwo6179D5N6tsVCRFUFB5dTd is finalized
Wait 1 seconds until block BLG3akiytsJqFHz1Ci5pk6CKUuSnkyf5U1RDUR11uR6d6oyaFDy is finalized
Wait 1 seconds until block BM59vSCTReHcJMtXQ5D1re8RQUtwGz1mz3gheJxFEFYNos7UZgf is finalized
Wait 0 seconds until block BLG1Kk6Af4DJQ7LD7QS6eEKoPcUXoCCq47mMi47gVcU9JTeeG7A is finalized
Wait 1 seconds until block BLsLTBKx71Ma3VCkXQTn61M3uoaz4W8VYPEnEWoTzYJ4JFjkAkP is finalized
Wait 0 seconds until block BLsGfK65juzeUZiLWJhPMuAwJKBskZTMN6JDhd7RREGuPJq6Yun is finalized
Wait 0 seconds until block BLR4zK9i26jreXYHV6dAdugPeSX7EcPRN41g9WYxssQ9nLqtRfS is finalized
Wait 1 seconds until block BKvyAEvvS8qs9zW3AXFim5PuZ3M4kS2pSz1JUgSQgDE5S1gkAYE is finalized
Wait 0 seconds until block BLBPRM9XzsTvpXCyPkvHXfrnfgCJyHzhWGvEj3TMvmvsVeedBYE is finalized
Wait 0 seconds until block BL7D2hcVXzAcLy7N8zaifBbnrzttFqzeVVd6fA3MmNxbfFDKvc4 is finalized
Wait 0 seconds until block BLuvtECPoU8sFVDs7Em6oQy8YPpZV1bcKDbFSGXcM5snA3Ai24A is finalized
Wait 1 seconds until block BKxSs7GNLKPd4AdmRW9oUkvJrVNTpoPnM9K9hMSavs4E3YpX73J is finalized
Wait 0 seconds until block BLQJ2s8kwvkRbMXjmzmf5CUgThwqfnzjkHcQ5gvQBKsynMjWoxi is finalized
Wait 0 seconds until block BMGBZ4hrTsu2cm9MmXrLjqoa3a6pZxkp42vcVZBTDqzq7aP61YX is finalized
Wait 1 seconds until block BMPWqzrwoA3ioTaUMEowiJjkBLryVFcoD9cNYTUoUGzWXPXQkbk is finalized
Wait 0 seconds until block BMKDEsU3EAxGjF4VAVVE2SktMNGeGDcjHEpA77KJnARbHFLgNEB is finalized
Wait 1 seconds until block BKwqTdTnEKJxnEpRHMYMn679pjDUZ2fLqsePhcDHJ35mGSuoMN6 is finalized
Wait 1 seconds until block BM6SELK3bUmkMhnsozVPuK6B6FQiW39CmirDKxgzUnsKtV9xBgm is finalized
Wait 0 seconds until block BLx9tn1Yft4pJ9TRgwMYZWMQJ4YDPR8hNB4tGcU7unHmMwQ2XRY is finalized
Wait 1 seconds until block BKzoURjMZxVdRq8eyoBbaxrnQHsx8fBoLckHWGNK2WQDzyA3UBW is finalized
Wait 0 seconds until block BKm1hM3QFdqE2eDG9nwUc4Nuh32KGJMzmYaxLebHcWdUSCSbBQa is finalized
Wait 0 seconds until block BL2Pfgxrc7bNMHBpUcbLqkdWFEemL3xAbYr1i9BLwTX1N2q1iGM is finalized
Wait 1 seconds until block BLCzkNbhMKiNFTqBtpQuWxu9ENKzfqstJKgkSmuscLs34UDZ572 is finalized
Wait 0 seconds until block BL57GewoapGTUYhVB1mx6yrwYAt4oPHzsp7u9XvuSy3mXwyvePh is finalized
Wait 0 seconds until block BLDU655beDFdz6oP7iLSaFic4h9mT1BQzdBF5sXJEGGNAfh8N98 is finalized
Wait 1 seconds until block BL88QN5QtuXctvwPeZseCQZzCoRMsitDhm4RCYCYSj2ky2trisA is finalized
Wait 0 seconds until block BM9Cy8GaAFbTepm8EBgGLis83TtA4Z63umEzfF3AUVD5JBFLBdR is finalized
Wait 0 seconds until block BMMbSFjQvjcofiAduEpVRDPMrozN2U5R5Uq1DwXKajYALEevty5 is finalized
Wait 1 seconds until block BKmDusoMeQx8rxCrpWS6D5Cy8FMzKRBvtXrc8LTtPA1Ayf3rkoc is finalized
Wait 0 seconds until block BLRuHDxQyUCiHYWN23qbex8wRaTo836Tv59i6Vk1UNz8johg3fR is finalized
Wait 0 seconds until block BMBYuj9EzibRHHZSQ2s7YARY6zpW1Q3hp4qytEGb7vjKbn1PnrJ is finalized
Wait 1 seconds until block BLGSndeg5ADueiVqCj4ptNVuxsTFFhKx31WNpCuj7qDTEndNH5h is finalized
Wait 0 seconds until block BLcKjcx4YMHCH2GFCsExPJBKygDt1CmqvUQM96z9GvfmZwGHfhw is finalized
Wait 0 seconds until block BKj3qVzxRc5BVDz59hNLDkZw6YMVapJQDzvffsd5tfTuBKbVYYA is finalized
Wait 1 seconds until block BLrvJvysx62B5Ds11uYYdjak42MucSZj8RnbgJqDk2HjkCJc5sJ is finalized
Wait 1 seconds until block BLf2YhitYmNRBdZG4CnEdCbovcVGRQP24SV93E24GmSjniEEC1c is finalized
Wait 0 seconds until block BL3bgbVjyygosL7LLjKhA617AzVE55ghWxLnVZ9AitaqGWiZ6KE is finalized
Wait 1 seconds until block BLahR4k3mnVMXDK5rMcLpm5pmVkQfhZsJKyxUxeC8bqEjMTo1d7 is finalized
Wait 0 seconds until block BLFeAd8ssDac4RZDxmVubnYpHeZwRepserQYYe9ZApWiqyGmJ4t is finalized
Wait 0 seconds until block BLoV8R4SVBL4uihFkNNkRoaw5gXzCQDcjqhmC9qass2DeJy1VAz is finalized
Wait 1 seconds until block BM12JYbH29tcqkFW72hXaYGKntCLjSd17BKrkrmrHdhnGCjY6Tw is finalized
Wait 0 seconds until block BL8psxi6j6EKqPbLmibNfdTBGEzSopSbkNV4zTrZejP3iwB41NE is finalized
Wait 0 seconds until block BMNuBhHneczA9SqXgtMeXTE1nGEEqrHTZDS6sFo4b4Y5ANtv5Py is finalized
Wait 1 seconds until block BLJ8CgCem1RLtSx69Rc4nDoLSkgSvp8btAXavvByckWfsB8hMWu is finalized
Wait 1 seconds until block BMSTGM4x5JGMgUKRfoeoLhFNNjy8jRfHLDZcGABm6SNYzp4bLUc is finalized
Wait 0 seconds until block BLECmtyz3w3ptsEjSBFaxUT6fTTTeJxdRJR1qyUHG6w7XGVoxNk is finalized
Wait 1 seconds until block BL3jWQTcR5iuVGy1d8Byems4qNDdw5XE9bASnp49FkeUXvcP4tV is finalized
Wait 0 seconds until block BMeYvSdf5nb8ZMEjEpnHc8SDHLHwmUChqJBjmekqy4gEpmVou8A is finalized
Wait 0 seconds until block BLnj2mCr53ntdKHaCF3pWEVqSpLiLRJMd2ztyR9ovSHAXjSEtQV is finalized
Wait 1 seconds until block BL9KfSyYMM3sXDNmfuwuR1sozNuGiAmyXuqFQJP4kzXJb65FQsW is finalized
Wait 0 seconds until block BLRab5AzD7GX8726Fs8bwhwkuoFcMwEaBYQN7Yr28SAfwWZenBR is finalized
Wait 0 seconds until block BMKLozJrePa48712zpctSZTpTFUbKjsgzDTpEZ2rRcvjUPRri5D is finalized
Wait 1 seconds until block BMUhGsiNLAeTSiU5eW4uZMFyvQ54XXyeWKAQ998iTgoVz2Fv4B8 is finalized
Wait 0 seconds until block BLwaC2bV4oURhUGR9b32izKbGBMdYPsKJ2W7kk7z5P6bpwmq8Dt is finalized
Wait 0 seconds until block BM9VN9mD44kAv6CZrBvYv55rYaxtXAKEKktN8Qb1S7bjN4tCKZY is finalized
Wait 1 seconds until block BM7xupqiUKogqpfbk1UudZmBN4xfkuaDLyLmPiM3o3HYSUF2B8d is finalized
Wait 1 seconds until block BL3s3rteYimQgmp8NdA8z49LXWNksnKNzwJBB7ZQdQVEpY5cE5e is finalized
Wait 0 seconds until block BMPJgdCDVewUivbAzGqWbXiE1Lv5GHTktP12hbsZNZBrFRuvcrs is finalized
Wait 1 seconds until block BM4gUT4QbYKEbbeuLcKq5vCwRDAFduL9K2bCxtKx7oCbmr6rpyK is finalized
Wait 0 seconds until block BMcmfgYcVRujvZrtw6qWdLaCxPra9XKUDFskiTxteajPBotuVsY is finalized
Wait 0 seconds until block BLmbZ99TPQLjJM4RPTMxPDdjfXspncYLLLd1iYcrMktWpTxdb2Z is finalized
Wait 1 seconds until block BLr943GR6m7mjEzNpQ9fmyWQk34Wqw5HSipg6xKfupULrUhWCMw is finalized
Wait 0 seconds until block BMPY21UPKZfaxVJR2PEwbWTY3BGsKeQgkVj86c3Taz2fgZHJP6n is finalized
Wait 0 seconds until block BMGYSvatadU3K8Xn7GKacaNUozjF3kgiwjBvnRWebhxzPUoT7kg is finalized
Wait 1 seconds until block BLmvaxoZvWQ1F7hPmZ7RCqM5QMnBJVn29t16A98aefBaLaBaPWz is finalized
Wait 0 seconds until block BLan1LFURPww5cP8CzHDuRRWC1Ec8HVhFpYp1JRY7QgwcVcprN2 is finalized
Wait 0 seconds until block BL3NZUvWePKiSdXRMvSuhTqHaQNwGjzqc2JmnRzmfxtqqm8dY9T is finalized
Wait 0 seconds until block BL2AWwV8qonvKxF4UGa3MJQrMGEG6efbfr7XJ7AVh1aTf2TYcfX is finalized
Wait 1 seconds until block BL1eU9563ccvPEdohmmrXLFPc8jyMEhJ7SwPUq6idnff856pV5S is finalized
Wait 0 seconds until block BMLRyqzhPzSTLLVguf9RvhwQ3ZnSrc1MXsRMD3ERo1NZ4WrCKD3 is finalized
Wait 1 seconds until block BLyFgygqX5Y6aHVUmusTJy3RgCjiZEfaKexvXW1Ndz7x9vUtU3r is finalized
Wait 1 seconds until block BMXohcYnwBhofBNToHZRUDWVumjBik5DEBmRxkkYEVSahkBheab is finalized
Wait 0 seconds until block BLbkGg36mZMa6nNGtSHK55MMMVnBDq5U3nbWN1bGXePcCwwQSeX is finalized
Wait 1 seconds until block BMWj9u7fu4dKPkAuE2gq7dcK9Erwm2bpXUH2jdLNvXHoczZFCXH is finalized
Wait 0 seconds until block BKogWtiGoGsujKZw9qc6R8Wm7F4DU4EhbeP2BhP7UywsmAvkh3Y is finalized
Wait 0 seconds until block BMY8aSrGs7oAdXFEmRCrcjBzHAeiUZLHneLh497xKRuMkHqq8w3 is finalized
Wait 1 seconds until block BKrWAxR2XCR3qwp6hVe7rNmNYaky8GrZQhd5puNXL4sJYSLK4mK is finalized
Wait 0 seconds until block BLxtNLD3Qo3EJ2ZfadJ945unXZU8wod6bq6rw5T52ZTeYrWUDDp is finalized
Wait 0 seconds until block BLUZVL241ofvM2CcXx1RVT7gPPWKzyVbC6qm6ELzT9nJdWWAmUj is finalized
Wait 0 seconds until block BLgQYJFnzSfXeuhQ5x3FnaZwMMxSAfKhGh21AbeqY5nXhMPy1BG is finalized
Wait 1 seconds until block BL2Kq5FN8HqxBx1tT7ghati7k4CiKb8fXk5PTsSQWqgBJLThvkX is finalized
Wait 0 seconds until block BLqGodNvCWaZgTXqMGxGYxmKbedLKn2axo1cHY753zo5Gxf5d33 is finalized
Wait 1 seconds until block BLfWVKU9BaTDc6ih3CDpEXcfBnhF4ohfvWsQF6W5QdbjeXbHniX is finalized
Wait 0 seconds until block BL2MqE6uNouYEz3arMnNbBxPGeuM1zUVt3Xb1RBDHf76dC7pCFJ is finalized
Wait 0 seconds until block BMVPYUHCctPj1JtPx9CVvLLSQ9atWkBpeuGSG7Fh2zWbmA42c4i is finalized
Wait 1 seconds until block BM76bidLLo6CZu6y852erVSV9Pf44zpFsk4iJoosLxpDSaENTCH is finalized
Wait 1 seconds until block BM7rgLH4CCLsrAEvhr8JNL3K9AvF2KuhifVPiZq2XZAg8VqAnMF is finalized
Wait 0 seconds until block BLZkp6D7y4UYm5VuyrpvQo1tPAZLs8iw4wxASHJXoDV67rLJ36Z is finalized
Wait 1 seconds until block BM5zvxR4srvEtJhvD9S54qWvHywuRKPMFARvmahJqDZbfVsDE7V is finalized
Wait 0 seconds until block BLaygV9bsByytQCV3aP4J1ARxmZ1z4afbmmChC3YWwZLGMWq3Ep is finalized
Wait 0 seconds until block BLcrq7Kw5QayN2syao1HMKNGDMFyWL3pG8giHUKAm5kpwNyD5pT is finalized
Wait 1 seconds until block BLPopch29iCxeKVZfo62aR4bJi4Py1AQ1QqbcwK69m7EV5ga27Y is finalized
Wait 0 seconds until block BMZ2cQg63g2SWQijVwV3uyyzj1BUL2eAqDueZgUormonoXxkd2W is finalized
Wait 0 seconds until block BMBxfJ46s7xiLfj6rGBqmtV8kjgJ9D1uALFLPcAZR4Hm3rXbP3j is finalized
Wait 1 seconds until block BKirGHqEKmrgKdB9fmc6Kd3SkLgCejGjnwgzLSuzUNXvYaeHdDJ is finalized
Wait 0 seconds until block BLgiWmwqpnssFxBvH72tpjZbsYsbhh4DLfLh5vefAtSCKgfJGhB is finalized
Wait 0 seconds until block BMUy5uhMfviFRDMmjx7Wx184ewGkGw22mBnVBHNtSUd6waV251P is finalized
Wait 1 seconds until block BLCtci1japxRQaH7g6mB7qj2DhKEjG1ZjNwY1HJhDDKxycY8BKu is finalized
Wait 0 seconds until block BM28jb2MnYSMY2xd1GCbSV19HWj3vqqkxzPotwuymzeXvh3nEfh is finalized
Wait 0 seconds until block BLqBvygWoLAKeB75HF2evJstgDph7Nmjx2d5umRusum5DC8RYkc is finalized
Wait 0 seconds until block BMesvddj4WX7bbi7DBj9UZ2HD4BnR9uXFEjdNCwbTCvoVZV6py5 is finalized
Wait 1 seconds until block BKodxV7JhW2bUmzRahkcNLSDcFn2qxR3ffEDajWadaeMvGqwuHt is finalized
Wait 0 seconds until block BLkjokoFfSbPWBiKcFLrKRqXBVcdBYE5iBge7iUGAy2gV6MD8DD is finalized
Wait 0 seconds until block BLuBTfE8sZ3BNoFhMQhzfkEPoWwxv8K5SM83MNx3sDResmVLfFt is finalized
mock_function
------------------------------ Captured log setup ------------------------------
INFO     pytezos:shell.py:100 Wait 0 seconds until block BL4N8pY4yGhK5tXsfRoWcXNUX5oQvxVDUNg3FYQLjArnPsQykxe is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLNLZ6bvgWe1UpaLQoH1PyyJeY3wePidHvZJTDpDbEFEMjW931q is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLtazqX5w7LmUpFuTZBQYsmq5T2sM9HvbfgQku1FcsYeHMNFjxf is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BL4E8FsziFAUd3DhZLvznaPEiESocqqVGVFxoo5oPgonPmkoain is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BM8qBXev3hptMovBAgBhPUTvpnwfL69ujN18i72yexo5KTY7tWz is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLmUBwqoPs8py6EEfLQMLu6UD7pQCtf2Pv4Sez3qQauGGeeRu2k is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLEZE56YrUNSKzdjTLdeHEKuEuRyVhZhrLvzDe7fURYKN3F4woA is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLoAPty2YWCAaUX9RgB8MszrDAeZQaPcErQAkmun5f26MPbX5L5 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLoktgyb2PrNNzFcRW4FrQZeoK3kVkagHEcmbjQMLwPMgBHDyzf is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLh2C42YDo3wrjQBBpNiS7kgjXsfbZZZzA2cxkuMBGUbvi5npZp is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLPvSa2fgAdfzwLBam8wFsvqhBB11ELU2AEw6hL9crojVHC5pSK is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMBWCbDAgJvhAgj24us5R2nFvSbTUwXxSwrkW3m8kLpgzYHzcqo is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BL4TFrng76PGD3ASQQ51akujKk4fSoYS7vFPf8FgANzP6eXBjAw is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BKoskoCpUEnDSPxBQSj7zq41bzjcxkAMP8BQrA94Z8a6F6Qn6h8 is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLZQRJK3voyp5UAnznsWJTG85qF9FZsmbpa5u5ywB29h3eNCTYV is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLZnb31YTQFCXNi9Le21bLrtCedVRG88Y9XZP3SNoT25CA5zfg4 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMHoLXRkDGXTFFgrqqYPUUqEEs64vgio9nZrBr8x1ceaQ8mNrNs is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLrTkQQbcf2Cct7FhMXCrCdjxJeQuTXQ6YqJjbDjGG6cayWdZd7 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLHF28p5zzT1KkPBT8E2fFQzJGUs8VhAEuu1qM2MgUFx3dASk6C is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLG5JSssG5XVkr47LRnxXdDzeUbaYx6K2Vt8kpvUeeApd6Qxzja is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BMQQ51pxaAS6Pn481m83LpfVxzWCijLqAHrUDAC64fSNKbUarZ2 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BKrinFrN4HvskSzYKJQy8s57KgyKnvDvMne5QeLFcPUiz3aP35y is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLfnSw6t8Y6kcfp4wP4uxVHF7iLxNAJ6yKNPeRCimw9RhdwiDaP is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLRsP61ea7EFeeD3hwjrKgdS8adne5M2ZpWyf3JaXn48jGGZe4u is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLjXK7Xz1rXyWKCKrBpEnKLhbGZBFRXmeZAKwF8ztkFEuoVK169 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BL5PoVUt8HKDE7ZZyJ1Pyb43b6h4nTT11jrjXKYQ1kGq5TuUmtz is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BL4gWiniQwPjQ6FHL1Yx8JvmeS66d7gDhz1VgsBrJTqhnAZEF1C is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLrB6qh1KMxP6aNKWSdPqwxWbrHUj7oigXDJFEeBZF13ErYT2tm is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BKy3K6hjdndcDwfL4qeUUwmSBjGfaAJvMm7ySTu5pnZSQkcMkNJ is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLAUEZUEqJHmvu77hhkDVmQtqdBxdK5sB52zC6Z4Rpo5ayS6Tia is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLU4kcfH1vDn4DaAARM7wSjqPR2Sr6qeu19kzJXEypLMJHNXfog is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLRLUjgTFYAZsiwGRFcT1YWtm2rsKiN3sX1k2KEgiNcbRMsFV5v is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BM2YHMDqsDSUALKcy9upDobyqMPmiebePG5P4YUAjjVVoanYWRn is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLiqpqhWjxytdVVGtkXnTEmcEiWvUxvYDFRjd74La3F76QbVaia is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMbSvsr3kvDS3hahjBz1RbwQVgHcFrH95t3aVCXGGwzVtz4byPc is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BL4Rp3LewUtroQgkw87JqH2VXfcG1AEiWnZizQEZdNHamxinBtb is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLjp5kbYgxoKGqm6bu2TTrXtDMnJ4ansAMChMfeNbkmeXf4vYkc is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLSQcQJbnRo8XFWtinQvgSofn9GsMY7ee499eRmVauct64BirAt is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BMbCsHLgNSZH5kemgLjgEgCWkTxPNLhZztnxK99b73M9QMAztqw is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLLPfk8SQq6kRzcfTnnFX58nPp4em8qG8wbe2TpSm5iakz2viv5 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BKjVLbVFNtg72Aj28DHzEmAkEePr7bB3w24e1uUJT5VZaPwfb5Y is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BKycngZFbMK4ppWTnLYNv68m1c4shtbr1okX4wDc4zCsMMNVJyL is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMRzaAUeFsZHzPdjvWoQ9fTTxQcSHAvjA3Vwfs8cwqMHp8XPcSq is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BKuGBG68UZ5wU6dGv5tipqbNRsTq7rzcKWFUPuh2V3iGU3WyKL1 is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BM4yUgSwjc7FbcKapmzhAMtQmgmtBLe9Qvyo3uGoxJxgWzzDaMK is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLjQAYvABYGL1ZjHy6xtm74WUUyZHqufp7EoJj89NWdyYyG3z1F is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLFt2mecXWeV5jJpyxehZbmEx1mZNMgFGHHqzcgzwfY2Z23K7cf is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLbrj97nfhZFYhdYQMZ9ifsoJF7DzAAzdFbYFYQKQ7tNa8jxWPm is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMFWzBQZwc2pgCxra5YyqTdQd2pzEZuBrutt7JK4Er6weT6A5VK is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLUYbx5Fx4WsXY2mJd1Z9sDnZQFw2WKNPF4J3ZictCudR2FcrDp is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLdqE7CBAJ5g6MsHgGBnG2ju4nr2TCTYadSvf2HdBwhadXiP44L is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLWcejcRrKZSUcoEaypfeFowybmTHWTP9vbyYEnjS7U4G1CYzEr is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMK46wMPuFiGCCSSDikyzfwzXJCiVZ23xAcKssnw1WDnZMrk2YT is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BKtTbp276C9JTES952oh4WgMqM9nQPgiRGfYH3v84CYMCktb9Ji is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMXBQshx4RRrqX8yQ7AujM1e3ymS14Vk84avkavWr66fqLCvi8w is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLnWZLMYwRgfrAoNMNa8dUV3Ewz1ebBxFxzgrPxkkDoJoTKRxTy is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLiyQ6DJ23KCiJb5xi3RiWMYtQEQnYed43kxhDRCYszdKZ8zKjt is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BKq6WhV9LdEuKXxvkuGT3JiMNCnZ9ksx3ra47FxV9CmzC3htcWG is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BKyAQ7GERKfUXRrRw8beEU8keUAKcvWiyvp9xRvPLMBvrAu9P87 is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLrz6kxviNZUbJEMfbMrqzesWMZGtti9DNstMc4bVhKj4CPwXgd is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMeosoMQnhD4fFsG4VDWRcFDc2ipB6PJW4G7AhLceDZafEGu3Wa is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMGEqZB1SESDGEV9PMaDYHSecGoscYg4oRFqMLELgDwab3rrXiA is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BMBBxF9un3JAhW2Ezwg3yCu3wjzkpb9ARrUDCf4ifZnubngG2CT is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLAzxG38wyo3pdPkBw8Umf8SstdRuUzb4BK8TE1WweaRBU5BcQ8 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BL1JD3ZiGxRj6Vieo5TVBmJx5ujPCjSFB9JPh3NLLP6bZq1bHiv is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLoZd2tvoKuAHz85iQDiyunAtA3ThfkbHzzgP9unbnhLMz1ez2q is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLdw5TZFtLovu1ZHBYV7PFYqkGZRytZhpJXUGKwx7ftfH5uS8Ez is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLKsVTBv6nSa7h3zPa2WJwGpZwYnVM9WFzc6m5z6iGjaagBaKub is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BL4GWrBmFQ9aXMS4NX3J49WFraR7ptUgyY5SCgQNc3YiuUcqrkt is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMJ3KsuC3iAhtzKvJNERhj8bbK6NNQuz2yopKevdaBTRC4THV1F is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLMMEq5fK5rm4KdiYnis1Jir6hYrtoux8opMiPwbFwK1Vx8B53i is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BL6WddVC6k5Ahc2z6FwUN7Ro8tFJwABKmM1UCW3ZVQwMJq7GJWc is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLbkxft9S5cBW2nw6kJkTH74hkTyYSSZCTWM4FzexN4vJ5psCmx is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMToQ7ZmZ1DW25AShxzGHo2i9VeWbbcJiZciVh1p11R2LdZit2K is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BKqSo8KAjuLuiaVAdfQnf6UpvKqjcYGK4gVDCwErFAihriKC1Cm is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLpn1Xu5o8RA7FmdNHFKVVunqb21FAK2BTmCTxUMWY8ZF4pZmGw is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLuVQdU3T4hLvFTy7GNjZEqiysABkYmNZHidUXCYvpndRrri7hE is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BKjRNbvvQb1BbDD9S2uJHNxbe3EespDNmJ3hSkzpuXGJYGWMwqv is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLbrc8NMdBJT4PFMzkEhZSyvZyd79FXTZC7N2cRqL22Ru9V67GB is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLdo76YXaFEcu97tXGbgC7jLczK2moc2B5FjWbu7Y6vHQXYcxp7 is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLFGX4LihFDcrarzcus3uR1kxkV8LYo8WY35jDGvp5qutqdkrfP is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLUV3Ke5uYrqkC19e2uysh7frXLQtyCu6q29Q45iStixQCq1KFz is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLmxC72ZrVJwwHDscknFsht6hQJSznxYHfMwuXeD6ahufRqALR6 is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLV1DtaEdAxYLbkdNv55UYptaEmZSswmo3a2iMhwWSHEZApwt8j is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLBSah37Y5pfVkjmQumgUUaarkKCfw2WnSeSnpi8hwUy2DmoQ4Y is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BKxPJ2XE6hQrTuP76oovN6BAzd6kMMVq4QS1y2ucK3qxjTytbwP is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLwXDyBH968Ls1na23er5Fo24mXWi4ATFHUe7X7brwH8JC1euNT is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLTyEoe6mB7hCp45hkWfqYserqMikJSiQnouYEQuhsTao2N4X1h is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BKmUWjhXQ3JvsvoCjrG5XHa6tVev55vJCkhn6TcFwvUp61xBQim is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLU6eN1XE5meb8AHyfym31WX3a3wb8Js7nE57R3fE8oFvwnVNWn is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BL35kyTX6AstG1NgkDy4UTggoH3aDM7LqjHd8NZhHZWkfwgVVwH is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMKKcWiSMMZEVQi6YfJGzfFeSK7k22ufvzFP1EeQNn5QZJAQyEF is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BMZ64apbavcV11PbZ6KyZ9vYdMnDcz2yGJqzbtQEPjT6WuFKh6s is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BKwQNxrvc561AxU8eAv7UZjHRqEwwhVD4v4AH82Ka9SdxsUG3e9 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLXh1L69ZJZhVv654Cq4C6WSJwriKwzyS8KKkryfJJdc1LLvGnK is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BMLGtCTPkP1WhJXvMECWBpv4QqgxKAKimQUQpGTUYEqrnLTXk24 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLjuqrVEgx4nYHbwGSmV949JFB5cTFbjJA6MKVXV2whPLFgK8NV is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BKjQsGtg9kM2c9ouXoLSsxNgMTtyWYfccC1qGzryikn19N8HvDR is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLiTRVXvrpzQpkenzjjV6oK65HZzaQyPvSYfkw2eCbWwhef15mP is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BMFRzifhJbQCubTk92hpvJurbK41W6znS84LgoTXoXnRrF891XK is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLscqFiDkpmHnqkr4WiRcKvVkS63H77esYyAqSHpNZpNJmRxpBz is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLoucPSofeCg1BCv3nDE8GkwTY44ZkH7JUH5u4k3UMevxWvbJDv is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BM8cnBweG87Q718ESApP5bAbAxWmV13wucvSvMRUBwosyfvNeTn is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BMSoGorYX84cgs5k9WoSCqyiVXjFJMKWSKk9YGtA4Rqswe83KEi is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BMTtGW9uScMMJL1j197Wm7AUvvGFCGJKabY7nnjHah7kZVxNHih is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMX6tf9j8NNskhQXKQmYJtaDJYwUdD8FFSSdCV6iU29bV5pb4eD is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLbiZs85MG85JoRFhyJc6NXEG5SRkrk2bBUZYaUJywWvJS9QFRu is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BMBX7m7pbKYDPUx28ioARCk8WAA7mg8aQGcpng9QLhw2Tnk2VBZ is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BM8WtchCxSeRBuLuD7f8wgCjs37XtsSHXwZGPzP8dRcm9XDJQJb is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BM6eYf13iDwrc9eqaJBrXoWPD5RvC1cqfmdHi3tNqHv7d4xCTcU is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLncQCEdcp2JcFBkQNVRpK4SWBU2fYXd7H1UbEYhnhkqzxpqbFa is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BMeKVPxuTYwY65HJ8jjwBSn4mpmjAS6xVjZcEKXPGsqLGquULwP is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMQzk8jqoP7tZCMdHTxn6A9jd3wpazC7Bzs4BJe5Dn2m1nY6TQE is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BKij1oaKWhDTNDbpnfog5T1NAw5Uc3ree7Xn1khsbJst4mVeSTA is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BMND4piugF81tjjsNw5VSLVtqUAWUEBxwdTaN3q28gDei4Cn5EQ is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLjg7e1B9oqzvL1k4QpfJ14UPsS8KxXepzwzrwVbcghRjYKGops is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLD8i8eMh9Q6DURNZbFK1eMEXpX4JRt58QqTVUZ3AKBmngMFYu9 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMaZfa4k4kR8LX6wC2pA5QKNzfgfUxhyzTay4C6jsVoeXVzq5iZ is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMb1RMFbLdayLmPuH6Yb2LCxHhbiXqeqPcExprNTfSXjUc7sLFh is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BKxUyvYhJqKLDKKsHNyPjkbzucokeZqi4H9CE9PxS49PCnxu8cY is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BM2bxDim5ap8EU6D7ZALUnbGkrieGFLPQjNXvMXZuhzSXZucQHc is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMBNmYgHbdAh1T4xwUkq4VDWWz2AxTAmUZH5pe2TEC9MrYvPyqF is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLEPjnQYkcoq6ZvUoDL1nnyQSSwFP6sK7d6BPDp1Xd6rdKMaQ25 is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLPycG5Gc5FcfPUKyvTjYiNog4D4PVqjL3M1kj6tc36J2JA6SYc is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BM2CD2igb7tsufUSTc4MKGyW8tGCupmFxTuwtnrDbUk3pmH4YHC is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLDHsz6PbFUZvRgNMPv9EtqHSpUM4VxcdbENfbupjQcm5hnPc2R is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMYTPec4YuzmRGCLqemMEvRPdmmpKUBk88ZwFf2wRe4iHUQ5xXD is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLJb9f5LPeQY47ZBKiL78Ss54WTg1k5RPrs1AdmCYU186FReLGG is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLNsKG7NE9KfWc4BtCyLr4XjE4wBvC2Yd9YHn3BTbXCw9dVWNLg is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLCbYdPW6ZhEWwcnBvCcXfLZieRWikzRTqbGZL5mPR5Y45WVhqR is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BKr27GpUUZwCkZ9bmJCuj8mc9qcLkoFEo7Y2CsqP8An7KfKu4ad is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BL5JZ9cEeRGtBE9oiKv3XBwzqHXfF2Eu4oFw33RSEQ36x8UWjRK is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLkGaJ26A1dqPmye1pTtgLbvkwPb5HaUEPRFMjVVCGTRSmrapfg is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLQ4kJPSCh6QV9jMeRf9GhgGcFihp3rne4eTpnAc32BJ56oTGZs is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLRoyD8pZecuYC1HFyecvUj9JsYrms7hLTnnkPhNk6o99546KxX is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLkZeCKSoSBTWheD2sqSb2BqTi31Qb9R3x56aMAuFivUkVpHUEo is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLnFz6jSPreBVQM1jBr62M5BTELXSJiU89oVxxvjZbkDH8D5JU4 is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BL4GHW3esidY2qtvGYoZtepf4YvQJdmZ74rxGmDsupg8BkNqo81 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLmosqD3x75PASRYFQsttbhJKkHr4F9NS23qv1hPymZzjkXoq4Z is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMXGuer4ycMMYouYYYjofDvZrraMeEoKmkh7hKX789f1ckgne8y is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BKjadfX2CDaN2vrBr85TRGYLeJsx55fLZ9bywq5TunhYKreegPK is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLvrfBc18hSzJAaSsMqtYpG5pN6ffYCbJ4FJRoTvxJzRttGRLwW is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMJfiaewbycqxjjwEeqm2DCZ8UEU1HA6NCwsF7c23pKBF2pehGs is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BKtmEJbwb4iam3cPmXMhB4tcJZJSCsmLMeaaCs5ACwFDrija1Q9 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLvwjz1dYYkhNe8YwGXM43pEn2MEZFcerFxy3kSvvt4mFLnh7sq is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLFYN82j4z37g95iAvrtZdZVxFZcd3kJprETtXxECUjNJtCDdeh is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BMU8nqWuEuaA1o5fv6maNjPLyVs2zgjDSpqq4VFw7TTCoGBGuyU is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLBUo3BpeikqZ7J1pKWXyRptq83XNtFrFnmEsGhfXNKfdMa9154 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BKwrLXT12aLZvNNkGB3ykVGdCnnUk8o9tD74WwAfLD8PSixfva8 is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLHUYrE3VgEmqhqLAuxijZXGSuCMSNSApMBXkcvgJMkZwzQ5sCf is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLsGnFcD7cAGvX4Z7PaU8NQoQHPoay5WH13biKnYfnp786xKxPH is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLG9PkASRbNnNbrJv5C6wFFHWfjU6vsVdFUchH5R7fTDfJkkxcr is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLHjJ9xeNwCpHPzE12RTayBAYPrfa1vKYumTYCxwnXbDrZzvBnf is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLKbbdwBepzr84SYJy8wSZ86c16HqF5BrocGNV5jEeij9qCbD76 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMGWPFY2aH6iDHtQQFYHc4ZR1qevdzHWE3HWAMtkf2Hsn1ygPzK is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLMYyEvMobTqtJepqHcg8SxDztHYkXGATN9xyc78VZW9eLJYcgj is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLCWCoiNUz4sgRDPKLss2ujb2xgKy2TGNDjjqrT3iTASQShYoHV is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BMci6nXqA7Z2xHrtMjXwVgeebfcPoYij2Zjfezxken3f8VBfM69 is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLZwuJ3efJ1DEG3qWXLTLMUJhQtxtVZfCLrEvY2FUYHyLbrAVeN is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLANYGNcs3khjhfJT1SQ5x1TzbE1ewPrdExDgQqiY3xtRbNrbaX is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BKuMHCGFCcENKvCSLCta5Xegcv8pRQb9wRmHDsQ9VLWyraCV4UV is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLTGZxnKMDJh7TXgnjmz34a47bAoiWbF8p3r5NcUNZnhieYjBzK is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLVWyjLAkkVzeMNg6tg6tVNDgvbigio8J2ygVmU5V1qjnh8FmJW is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLn7e6rNV729Yb2PbL7CaN6Vr4txhjgNueCaSShP99KAuzhCwAv is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLPVNKhRsPdZqQfe3junZ1gjjkBSiXmANTDNxr4Z6kKngDejPRo is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLFYVAdV1XULZd1XSvTfeSRxaNUJNMUtgidMZimk2sit4VMQNv3 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BKtZMZEvjjqKr6uZ9oTPZmGpT9WPuoEKRzpnFUNPiJiUNzHu5Ar is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLpmEDrAWtBioxoqn9pDJByQpCbruAGET2VoYgDvGA5EAwRkNbQ is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BM3zsxrWrnL3osc6UrYWsAKvkXdqWrW3iGxz2kCZaAspHUD42Rm is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BM2zpqBctwZdvHaxoJVV7yhAcd1nMXs2Z5vGtXv1MnZpkK2ijuZ is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BMdzcqAqhtrW1N44jV5BAqX7JGVHvsRS834nvj64LEPE31G9o18 is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLEwpGeYMXtccJFCGQFgFiuBSe1Y4exTiJ17jnBfCdtoWZJTSXT is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLLwNoiyngDhVqHK9N5H9ifhH6vXQSmRHQBfToYBRVmZrERaJC9 is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLAQU7EvHqtvAE7BQa21CMGxmWh37tTo1vrfCLdbiQ9t89RPsWv is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLignE8WVLRJaUfEHGaC4imQA5A8Ky9XyPnNL7gji9xJAQaig5T is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BM374LGA7fXigrcmcDqbBe6z4kCWRkJwvT3RigdSTfsAvukVFDk is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BL8jYvYrbWm2gwNN1tUTnqUdtPw73dHvX8Dq4FVpR2Uk3yTYt1d is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BMBhapwdMLx3Sgd1Fxwm8q9NafijELcmCNYrwRrfFKTdU5d8PKz is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BKkFs6y6XqMYDtdS2iZgVDgYpS3njwTat9eKenWMKJPdbtGGDSh is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLwsAoHQN5zFQFndb4jnm3x2TGyZhL2ViBisfGMconC6DDWixJ9 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLYBDRUME768vkbeoqBS9CmKg8v3KNHJdk97so8GeYTVXQ9Lyar is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLJN9t31TdTU2VYFfqCGbCWcdYE4a7UJwpBmJY8u5GWZqA522ZE is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BL1axtchm7TnQS3BipdbAxkmjHLkHBEP2swCM5VqKgVJay7ryHP is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLHgvzMPojgF1HaZ6PZCbwYQtDdHS95dLAe6PksytsY5monJ7Z7 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLyzUwyctBvsgBa7RFcLUuMqgshiRo1C5awTnGqU1M9DHtQXVbD is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLNzZhD9CacfMx7kptNH3hSkkJCAwZY5XMYVL4onwa6YtfjWAqw is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLh7sGujgfrbj67rKJS3pe2LJekS3AFfZoRZgJBJHUuCFEiNgr8 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLH4cwq2B1CESapr5am7x59q1wwqZTfQJgjhUc6YFdSArm8C49L is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BM5YGrgbAzzw9zRccc5Urm9hGXC8zyTmPyoSCkiEum1xQGD6bRw is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLE8SQBa6LCe6SPoiGZDp6BEyqWQvHNoFzFk3fQyL7uMFkmRzZB is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BM5ia2okqHZ52L3rsYatVHvrvUHwuHhrGeku6u6MxH11Rppy9WZ is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BKzGgMSvjLHXkuxDBvcToR67DWqMDnKMZ6MSHiYMA6cNUxpbqN2 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMWTGuRUDm9hbZfGyHu12aUih58qjQESZMEyCu7ZUQxDkhWHFXB is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BKm5HHtjgZHJ153s6P2GrtSqwk8qW7Ct8ZDAmTBcV9bfcXn5reu is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BM8QPDDwwWVr45rcPKZWtBB3SAnytRizkeqpKmPzrTk8HbtHAgm is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLMTRkx6dWRDoShVSitwHefPopx8ioURLZUW1VB8fSNjKapSCxb is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMRAhvbEqxHCQbFG4jqmzWRV3t12M73kUmcaWj8gNw9Dvzo58TF is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLu1tUKTydLNwX7YF6LtLvx7xL7uaXvnppyp3WBcywtV5vmzsxz is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BKt8frkrAUmkXWvpWJALqpN5VQcd5qTeoMMFYjLH5evXWGhJSGn is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMJaNLck2PCJgL34XiGGdaNKxquaW1xFw7NvN9CFCi6QjJooU7H is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BKv3d9kE6hHp5WGvPWTZEMZnVNg6ojczKwzk7D82Psf94jpJhLj is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLzsRwisbCJPPjytJRk1poD9SNo2wVkA4NiGUV9eEyXQD8qAtdQ is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BKqzAcT1MRYnrKcGFBNNpjuk2sjdV6xhwbewRd2ZdLRVW3hXoKh is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLjg5cvb33UHG6kCggrPyKZMijjeraxDQJpwC2D2PNvzUrmga19 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLcHZwB33MYU3YaDMM35n5Yx8Soc4KxAt7y5LgHVLtL6mh2Hq6t is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLtWsmkDnhZ7pSi2HHh7QrSgGpCRuUNkvGMr9EMJJDMtkuAWfa5 is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLbXnY74kEdeKCQm2QL5dHRtwyp8ifrGpvKRLzcYzpjszZPiRE2 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BL6uaXmLiQNWMXzLvrdqY8K5TZXD4bcUG152sYu52okYcvZPwzU is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLJmAtEfaqhbj7QKJgo4p5s8Z3NWrb7dvxPvgri5Ft4c95Cp8iD is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BMMxwWPrNAdhdrEwnDD9TDkxQY8vsshi9n7VJYGa6Qk4PAGn5YQ is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BME3rTCBCCMwynKwZbSGAMxZ2G2V8RKpYfxLbt17fW87CyQ3eNA is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLGg2UG1ZFq5KWw81yTMt4Q1KPsWpzC6WEdXfSTRGLe3B7petPf is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLNEC8EBBLj16wUgGnDPL9cGhrD7hDtx3vt4U2FbioUUmydoNnf is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLZdpSnBx7rSmBi23152JNcMso9VXBStnk84jgwxC6cJYwa5RGg is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLyH475XNYg2GEc1dDrL4iY5jUaHy6vmCQ14EMDiyEJ4chPnKNQ is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BMWeqfRwqxvPiqDVu7TakKMsAXKqoDQidbB5ifxjsxHQxrAozW9 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BKtQGsDyL8HHbuwP74euwMLUHfUdcVEBh9fWLrcsSWsmCpMMs34 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMDhymB4ALVhrFzQvz7KCL8PaXmuNjrkaYvUP4YSFrR6dueaATk is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLSecxjrBnt9BDrfNnVQn6Wuxm9mdn7FWG7dH8dFr4BNMTayvFS is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMKsbJmyzB4jR1CkfCf9bpCBdtU8o7T5nFyg74J4r818yVCKcrR is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLqLR3ZwoYcECUviLQAEg6xrPwtwN9nnrrBibWAwf4c8tNFERC5 is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BMG3fkJggvJBrzbTCNbNGMTmXTDNihW6ik4YZtqKohaWyWsYGpw is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLdHgKseFTZiGnR13gwomkkGkekto1cDaiCCkAF5ZLDUEqMH4qe is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLhPCttFp6YSLFe782yLXrZi2SmBrutrPtd8WTLZzn24LQTJqN2 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BL5HVdUJ5jbXdRRp8WgBSnPu6NRPWR6MCUvDLkAJYkh8dvBuz3i is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BL7KTWL9KnAdaMijUkWXk4h8rJZLj7uiQgkidDNAtbWdaD42kxe is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMA8B8P4rRCoJ5TiC4cLYopYr25rv7rJBtRd2YAJnvWajMvzdsV is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLQFqLwPKjMgQWULBccRaEFFSA1aPuCF72ChtHt96V7gNFMqu2j is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLNNsAUyRnyLwJ4GxdAwF3BkBuWgSQnSKmnFcP7NzKg45hrwKbB is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLoK1Ae8T2DUZayLFdnDok7TWXiWZ58rEL8pKZTpSEghGsBFMn4 is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLFXVMTsLgh2YJZByeXCZRzy1CJoNqFE8PF4w6XwAJRzVYUaM2X is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMNkLR4V5EE6rCsBkcbXh4e174q8qR3FELeHGiNq2xaFDywiyQf is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLG6oZ2n2BrCvqMWbw3v3nnodYdP816CZoFS6AqzLNKTXqrBFvS is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BKj4c3TqfvgG4wiwcbpWmMLdYHPAB2oQTihEerFcjjrgCD22Drb is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BKijRyvH2KsJDx1A36ZG8NxB7MeKQypQD7Fs3vzJWpEgxFnFUS7 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BKnAK5z9SvYrArhb3sqKDitfWCLXi22MpeVNxxd87pfRWzhAdDE is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BM5z2nyX3hjUhETVXXWGJAx3Jx2Jy7jQkTh2Ni9r4sp8Kdtufwc is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLdjysjsHqdu4ZMk4nc8RXJcLnvhSkaEAdGQn6a6wbBK4j6QSVh is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLMsc4GKda81ioq9WWu2eQhwYU348D7CgvwNSN2JsckHqpCqRmw is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BMR3y1x2gjTqwgTjb9LTj4Uy5aKZJerQopphAPvSC6qu8qdEuvH is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BM3VDiEsnJSNsSzBXAUwAPfhMBKrEX6MVkkQqp2fUPhtVfBNyd1 is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BKvBVZ66iB9jBQvturFfVTvs1ChuTP4bfTyZExKyaTitLtBM96m is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BMdprkcyYpMrJz5GquFeqzRMqBGFKnjepn6fg44tVvZNRmp9GDn is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLjWBnxyVtsw5VU5Wt2k9oACgZVVxq6dTLxvFCNsmpWqEyyRATo is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLMdAv2zMCNaAQzViE5YaS5rjNkgKmQYYY78o3iKiZna7sDd7Vn is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLMUvjofizxLESuwH8V8HejdHhvnJupt2SYNBbdhAgrfwRfKSJu is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLfeKVYCKNxaKjLzKjku1Jvrps58NMFdd8Ky49Mv5phU7imdwR3 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BKqaMSfwxppCL87TTzFprxz2hSZuoZikghC8u6xhuAFFpejK5bz is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BM5a9kAoDAF4oFXcVhpdzdAyH3NBhaA7BLoXjWBtQ1UPr6FqNe1 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMSH3tURSTEawpVTkCzCK2Ps4AvUWY5cBct4CaPwNRR48NRgqrv is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMT8d1jsEKWjQFjhSzop9T8W8CM9qKUXAUERGDwDYD5ryRv9W8F is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLf8PfNFKRHzrVXdWxGpSqBLuHMp8gxJ3FocEeCmGU8RxsvpmmB is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLox5B7U8wxwwi4MJWUt7KHqpttqtcBxzkBLyFNxLRGsqzm5bvQ is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMLbSKibdmy47yycR5RxYyS56QRv2n12CSiheM1btWydPa9e8n3 is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BMAbLdsATCdSnoii6DQTUg6oL9nnjmsWsVaK7XtJJP3x4rm4DyF is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLjU7bSpworgSig2UUKqErzBTbPUi1hLz1VjrM6CyrYAaHArdJU is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BKtf53QSghJgHYboVvxHc2njan6hd1DHfMm1mXZEaFYVKfJYYhS is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLRuAdKBNMdep9vvoerDkKZ5hWAXCcmZ8aDfFu1sG8FWQp83Q4J is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLmgDiALVPMbFpKi6rUpUE2Gp1aXdv8G3NoT3crHHcD5nqdJY3y is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLiVVCbAAeLsqqVNZePBxjsDmypVCFttrKwwFgMuswmkThS9745 is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BKsVdCE9zjS6UWzEefXAcCdNY1o8UkQdvH369dUfBnfH4QTh8iY is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BM5fQQePDECKpBtu4ChC66pBf9eJfiiVrbbZEi6wkcNbNVL6PxT is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMTwXTrdpqkEAAaAh3BEs3sRj84ZCZnrpNk6dSfmquXqwBBX7be is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BM8cGKHbBfiXWZgKYPBSeVss35QFYYLgVihtAVknTyoc7BP3oqK is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMJkXG3gVLX8M7qM7ocRd21DBp9CyWboixK6ykM7HkEgxvtaC9Z is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMS81hjHUXJi8U8NpveGaHZecDJUUGNRN4qZP7fd6Gv9hwQL2qe is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLmaM7Mf4RWJEV1L1F59HofSSqivbYk6eURZP524LuhfNtv24Jq is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLSk88kooBqW68pzam7ZZi6Y79X482Nj7baQjaSPgGf3yN1aju8 is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLBdLBVULUssDorF7GKwwqNZsm2MxAGGpY6JBh8FkXyyJpTxrtv is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLgVAd4n6ctJP9CJpjSYWNh1Rv3NdHmFhjhugqNvFd6YA9mehZs is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BKkuKgJk8iDi9xaC4XJ4hZDMUUJVaaGQ3HWUCErTYyUe7iQhKyH is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLc5dn883Zkj83ovDxiSrp84MGP5Zrz4tHBJmouqEuJPrsc8GtV is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLicCwrF2A5w7JafiDd6tTD2MXCajwGpgHXDQmGQZgfSwo3TX8n is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BKtaWs5yEw2HaUJ5XGfSdMqaqQkW79CRFX4nS4W69kMg3Hf8ds5 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMNN1rd5aG72TS2FVWnt16THUZqrZJcuEkWNVW1sQP1LS5R66oe is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BMRY6Wk4gMQttZMoU6t7rrWyXF1LKcmC6928ffwqUtSLpVjz7PF is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLvgn9ET83haeuxTe29y9Aj3KuyuyShrxkGMzvuH6sDKNXjUqQb is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BKtzisfweZhdqeWxJ6MeQQCdGX2saSn4pbHQMY7Foo8s6bGgfJq is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BKr57XPDKgPGoPNNN4gAaPwxC8amZz9NuJDfQsZqBG3f5456xYn is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BM37wvCrEJ3edbr86JxFBT7HmCFzcfjgCJKR2vLiTq98JRLzfWf is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLAyzkKKGCEcWL367E32Nkz58KGy3dJ9txiuPSakNzJsNtNA8E7 is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLEVmgAicJMx3iPFy1vkUzbYRDxNobVRKK8JnyDizxKPnYiWk9S is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMBE9JBaDdtYLyN8ZXFMbzppiaed6NR1AgxEMjZyEXGr9PmGmKb is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLuQkB8X51ARAgdZwcrzeGKYchfy91cBj9qqFztvt3veNtKC47j is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLKm1FLWtftVfnjRTMyBndi8crxnqY39hFni5fHkxLFKvN3z9K6 is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BL4Dw6W5FdHFBGvcgHomdrfuQRkbMmELRVhmsrcyiuEXFXht6qA is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BL4Gt5KxKRFG3MAWVPq1Gq6PcERWLhbLH8FGJvCePhnaTWAcNiX is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLZconpf3pid4sq7HuArNwVKjh1iNfzEChZVE6nF95EBEe5mz53 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLk4fAhjhLjuhpZzUGJMqL5NyWcLHmKWKjoDkefSdKhtN1MqaPc is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMPTDfPXJR6zeRwEfaLqGKPU1yRxTEHomHh7B4dstfP6fETjJFY is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BMTieQjbJAhdPghMjUrTGKY1fM7tPCi4DQNSyU4xCt6ACxcWdks is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BMcAuu2xmw3KCzSHqeM4LJNGUyzbEw7nnJPqjXUceYVwbyQUtLg is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMCnds8nDUF2bgeBGo4NCS9kGzxSHDSiopVKFn3h7qobDuf3p4f is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLNEXVMcCtWv2iNFbA6mGSgmsYPLEumT1Co6frTQSPmYtJ6ACCi is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BL9tDrkaLX8kg2EX4v4Z4kpy6XZaDWDjskE76CzAMbrZwyMhkVJ is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMC99qoFEFHcQXZc7TuSxXhNbjWx1gexxKYkJAyDa8BchJbxU4v is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLrZ7GJ33b1bKxnDs8WwRj6ro7rneNihDHKkdZGESXm5khxq4EE is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BMeVKJxLF3AkyjcHESo6woG5RQCbUjcsLwRWTJz8c9EuF8jCdWn is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BKxDvcBthaK5AMQW7wNxUgAdLFVTxicmtfR1gTcEapbJhhtCsGe is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLJ1EUVkq55B9q8JMYEDu4bt8wQHD7Hs6CVbhqoYCQB76vEyS6A is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BMLiZF9GPpkkTZtTwXjqNHMczhSdVU1JHGiwDnFKraaT6TZczbf is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMMzGmADjBmr9LB7qaHAzm7G6ZyW9Afqdd1QWSo5KXuYTiE1ZHM is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BMP52sRRcXGwmG6zpr6BKPEYMqtFVT2M399LH5yXYjTo7ss5hCs is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLfg78p1R3UJ3EZtkZQyoi4VhnwdGvKLSqkajH2U7uBoNwJmjWJ is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLvcK6q5EgGQc9dHxSeebNVE7iMzLFgrnMeFFmVhFh5Jqiqncgm is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLCrGoVR3feVjQ6pJv3pEKWEGBV3qedzy2fRUwycrzd6ova4Kzi is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLBZfDw2MSM4fj5yP1f5ZhhSCGete4J52BDQmx4oHnJihPAHWda is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BKqC1X9Rg2RoHHLxoHwHXiL1P1UCAWJhPYtLA6eEdFhzyLj4KBJ is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLfBXMnBXcuN93SsjjSWkuEH6B7Yw78Uv3XAtyJYNkJvKUh1BBr is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BL7r1YfCEQWZYms1eH6J643Ryw71qYHBYavpXd8o6TSeo2mn9rN is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BL44ftCUYios8rjBLeTFDvoU5mKCv263MK3LCyEsetSwpFgzJG9 is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BMN6YnzxWCZUWGeWgMCbpRu2mDaYZdQnTHirRQU6YrgcRJunPyc is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLMsw16adTnDM1KpdfLmWumJgLFXggFfJwZvsrNynofzxBeeYXZ is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMRz7gRN5h3cvrQjL8sgEzE6QiwgmeW3xaos8Fk2UzniULLQbDZ is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BL6NYb5TKJvNBWg5YvLmKgkFDwa3HArxmgSCkaepJX66wiN9mbE is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLBUCQEX83hDUZQ5eQpvU8xJrFT2GsUK8qNEU8r2paPapS7ChxF is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMFBXnw5dEApsQns5BVE5qPTHNqTa4KJ6iCC84CURxJBJqnFjPu is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BMWCP7GSksQFVFo691PZjAhpQZcw3GCrwawciAk1Dfkn6NLfn47 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLLeMkz3c7cbxdeFPJo9uP8KAxDwC4rkXaBAK8cfYMVCZ3PHaHc is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BKqJJ2Draos1XXqjG62WowD9E6QH557eQNpBdPYFWvohFuCbiq5 is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BKp4ueo7hRbaAmEPEv95iy3AxKmCTtM5GY3yq9NDiHqHiv9JUGP is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BL9KhGmb69BX2vrFZgnc1DUM5Fp2rZdNrK4GXVpDnrvRMTDBw1r is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLTdt7kTtvfKs9JJXM6NRKsL5BDurWduizEvFdxy7SYv4cvNLNi is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BMCMakBamcAkpErf2VzyVAZvGEnwRugEJzaS8P2fvWpgrt3of3u is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLngtYpVfTxD7vZWFa12eY457eGtoKGn2JVEputvkJtjw1xYCP9 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BL6mqAU1FQRqXjGZcaNYrgR7EUy4wobPvYwsTPZxb7TrWkkLpgx is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BL8899Nj4GDn4x1VVnJSTaAnqBrGEySx911kFUMxppbmDu56w75 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BKq4bzKDC2fdXwN6nfhd3mmBVRC4TPmc4VyxnGNETZbGGy7cHw9 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLwHtcBbHF2J95EjWQeBcZRbCEFev6H98QhGUkpYU3SdVZWpHBj is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLZxUJYxe2tp74AdT8pVVfBKFt3fenjS1N3nRB44EWd89CeB6Gq is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BL3tBXrRFBn2sXg4w9WSQ8vYeRAwmQZ2Ht4zzGtJMhL8FMZEnd7 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLWAZSvqdaGnXG12nRv6RJ1eMp1f87afyrcXiFippc17nEXrdp5 is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BMAXdqBytYRpKFTE3mACFJXXMsCzQrb99Be1DrtQS3o9vZSA8ax is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLBfjSJKQWSmAB7nSghRa9yNjgfVfUjwzaCRbKUAqxHdxp7kYyU is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BM4dJtTgVWiwTYyHvLYhmugiLqYNYuivwbm6JfNiAB1tv5SczN2 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLt23hUed4YKzEoeoApR4c6YbnPCAKXcACU8NyxdcoeXDnHZQxT is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLKZhAhK68b2H41W69Hbe7UK3uiXoerBb7oqy4haEbYpYvVupsd is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMWyoeRL62v4okVafQ7NqLtmSYsVURrDRUbSe39vwUHVXgJ61S4 is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BKoVdKKYctaQN87TuWrSN4eubCHRokCxgxbo7cAv3khL8eXx1JB is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BMWtY1dV8jxXRm4ataH8QFgKxQ3EKDWJL7UNQsQQuNvbCPhAjGU is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLSqY4JjuYm65QYeRBPYDRa5FptmaURRyAfGDmTKsUK6Uvp8uGd is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLJpu5CTrYJdFYXA5bbb13WGZ5gzLGS2YM1Qomh2wVWLj6W99rq is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BKuoanmVTvUH345HyDzqgCzxV4QpnqXxcoRr21Uut5bcZd7poN7 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLH221uZnWH4QdZG7g6yyMcBitEBvGmavV3MXN4QuwJsBYooM6Q is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BM2BNjy9jBJ6ZA9hHqRLeKqvcjdCq9AFNapV7zN1h7BLrUcLq2i is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BMH2ZuQ8LwXV49xi9pVLkZfwB5rhVrZNzN1xHsUT6tHxiCQCFeN is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMMH6SuoUBgYZ8PciXJ7FXguhASDhxPxSYzAhhn85veohwDHAnc is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLuTzNyqKpJB21rDULBHABoXZYRi1dAeDfwpHKv5khRJZj5Drki is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLStcUvxPCxTAj1kTFJih8KKnKFonYcDk2ssfCoDqXBNtS9Z8pf is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMRxPF4SbCJdvBt5wGnSVLPrhqRMD8C6rTitNb7QcmPaHVz99zL is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLLPTRJnKi11R4DTc3brhDWUcTfL3eZKexJVjmFfthgVD2DYZwg is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLtjoxhsW4XYG5Yd8gqvhAxY4bsnrvZLZGeWNwTJQGjKjgvv4dR is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLy7RCYnFyWEBD3iJq6mg3J3BQk8KbnefS5PVeiPnGNqxoiFjfg is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BMX4ciqkQSeZLfeRZhDt8nu5PqLt3ivAbQjQ46CqQKrY2LveLD5 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BM1MCx2chW2JqHHPmsfQX5Ro7CGTcbo5vvhDnueCUV9G6LQ2HK5 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLSq2iaWQC1RHz5cFZ2gq53CwAQdUcC4X63KUSxkensT3CHJT5v is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BMB3sf323JerDYBB3W5Ce3grURMN6Ei7oa4xvc2KuAey1QbkATF is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLvoR1NTiaSmBYvDX43wmjqQr9SVdM1acTHESmqhw15FHvZFk3p is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BL6RZwzNePTx3ztgGJDrqeYvaRSxWAWja9DzDF8mA97BMmWTUAP is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMRD798g2NkLJjfgwjBS7wnreiKW2Yi7jRLZgWPDM5DLuCbpown is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BM9JH2PnrovTTytHTBWxotgvy8UJXwx466pqdx3fV2wJpjzAKFe is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMEJq9uXKPtjD7EK9a9Q7x3TXc8tkmMUqvjeLuY7mnXh52W4nBL is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLzpgWT4BWEm1mb3tegBhy4nNKerG5WUKPuNgFT1XUGxbvU6K9k is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLWqLZWHnuTay7eUbPqKMtf2iB7WEY5kkfWCtmUzYFSu887ySdm is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLexkgAxxQ1Xs4fGsMkeHebYuuwVtQ1zJeSVoT8YEJyNh1bFsZg is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BMXak2aGJjqBbL9qMGpsQy91qQhUmETGetskQMzdp7ZSgjdP546 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BM6N8KtVvarA7JvhEBMjCAGkPP6TrfZxf1ZnvAGjK68AFcz6sfr is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLPkyMg5y67xjL8nXbAomfqduK2GCPFrNenRQ9ywrmKYDY789Wa is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BM8r1mqsNECuzvBGGrnkk79wBMDjVESyS1xeBQ7ikm2Eiteh5pj is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BKnJot2pcDNp8UiokpAxeLpfwX74h4M47XDgNnMExhjzs5bABrH is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMY6q8ijAvwrLqFmNFw1RB4iUyqCBNLS6cAa4h1MUxXbRbiKnWN is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLDjLwSZK4xbU3z8UJfeNgVNVorS5t85Pst2zzUA7EVmtYnvN2M is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLnodZpsziYGztSUVBMD3HRM97XjAvbmoTXqd3sHCTSG9xrMASK is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMcGVQWtobXtwMD1qevEzTJwneU7KLz7VFm66rAnyBMfkax2PGm is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLadhPJeYTLYesYABJ6msD752b4yLDCXcmTUDYQFoSomAGKz9tx is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMQ1sf4WmtjNQnzt2WG3PxxCknfMj4SnkjUzd1mygrkB9TkTWZq is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BM5FN4UyRwqZbokTzyZnTJBg1dkcwo6179D5N6tsVCRFUFB5dTd is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLG3akiytsJqFHz1Ci5pk6CKUuSnkyf5U1RDUR11uR6d6oyaFDy is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BM59vSCTReHcJMtXQ5D1re8RQUtwGz1mz3gheJxFEFYNos7UZgf is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLG1Kk6Af4DJQ7LD7QS6eEKoPcUXoCCq47mMi47gVcU9JTeeG7A is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLsLTBKx71Ma3VCkXQTn61M3uoaz4W8VYPEnEWoTzYJ4JFjkAkP is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLsGfK65juzeUZiLWJhPMuAwJKBskZTMN6JDhd7RREGuPJq6Yun is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLR4zK9i26jreXYHV6dAdugPeSX7EcPRN41g9WYxssQ9nLqtRfS is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BKvyAEvvS8qs9zW3AXFim5PuZ3M4kS2pSz1JUgSQgDE5S1gkAYE is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLBPRM9XzsTvpXCyPkvHXfrnfgCJyHzhWGvEj3TMvmvsVeedBYE is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BL7D2hcVXzAcLy7N8zaifBbnrzttFqzeVVd6fA3MmNxbfFDKvc4 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLuvtECPoU8sFVDs7Em6oQy8YPpZV1bcKDbFSGXcM5snA3Ai24A is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BKxSs7GNLKPd4AdmRW9oUkvJrVNTpoPnM9K9hMSavs4E3YpX73J is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLQJ2s8kwvkRbMXjmzmf5CUgThwqfnzjkHcQ5gvQBKsynMjWoxi is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMGBZ4hrTsu2cm9MmXrLjqoa3a6pZxkp42vcVZBTDqzq7aP61YX is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BMPWqzrwoA3ioTaUMEowiJjkBLryVFcoD9cNYTUoUGzWXPXQkbk is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMKDEsU3EAxGjF4VAVVE2SktMNGeGDcjHEpA77KJnARbHFLgNEB is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BKwqTdTnEKJxnEpRHMYMn679pjDUZ2fLqsePhcDHJ35mGSuoMN6 is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BM6SELK3bUmkMhnsozVPuK6B6FQiW39CmirDKxgzUnsKtV9xBgm is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLx9tn1Yft4pJ9TRgwMYZWMQJ4YDPR8hNB4tGcU7unHmMwQ2XRY is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BKzoURjMZxVdRq8eyoBbaxrnQHsx8fBoLckHWGNK2WQDzyA3UBW is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BKm1hM3QFdqE2eDG9nwUc4Nuh32KGJMzmYaxLebHcWdUSCSbBQa is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BL2Pfgxrc7bNMHBpUcbLqkdWFEemL3xAbYr1i9BLwTX1N2q1iGM is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLCzkNbhMKiNFTqBtpQuWxu9ENKzfqstJKgkSmuscLs34UDZ572 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BL57GewoapGTUYhVB1mx6yrwYAt4oPHzsp7u9XvuSy3mXwyvePh is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLDU655beDFdz6oP7iLSaFic4h9mT1BQzdBF5sXJEGGNAfh8N98 is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BL88QN5QtuXctvwPeZseCQZzCoRMsitDhm4RCYCYSj2ky2trisA is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BM9Cy8GaAFbTepm8EBgGLis83TtA4Z63umEzfF3AUVD5JBFLBdR is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMMbSFjQvjcofiAduEpVRDPMrozN2U5R5Uq1DwXKajYALEevty5 is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BKmDusoMeQx8rxCrpWS6D5Cy8FMzKRBvtXrc8LTtPA1Ayf3rkoc is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLRuHDxQyUCiHYWN23qbex8wRaTo836Tv59i6Vk1UNz8johg3fR is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMBYuj9EzibRHHZSQ2s7YARY6zpW1Q3hp4qytEGb7vjKbn1PnrJ is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLGSndeg5ADueiVqCj4ptNVuxsTFFhKx31WNpCuj7qDTEndNH5h is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLcKjcx4YMHCH2GFCsExPJBKygDt1CmqvUQM96z9GvfmZwGHfhw is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BKj3qVzxRc5BVDz59hNLDkZw6YMVapJQDzvffsd5tfTuBKbVYYA is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLrvJvysx62B5Ds11uYYdjak42MucSZj8RnbgJqDk2HjkCJc5sJ is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLf2YhitYmNRBdZG4CnEdCbovcVGRQP24SV93E24GmSjniEEC1c is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BL3bgbVjyygosL7LLjKhA617AzVE55ghWxLnVZ9AitaqGWiZ6KE is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLahR4k3mnVMXDK5rMcLpm5pmVkQfhZsJKyxUxeC8bqEjMTo1d7 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLFeAd8ssDac4RZDxmVubnYpHeZwRepserQYYe9ZApWiqyGmJ4t is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLoV8R4SVBL4uihFkNNkRoaw5gXzCQDcjqhmC9qass2DeJy1VAz is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BM12JYbH29tcqkFW72hXaYGKntCLjSd17BKrkrmrHdhnGCjY6Tw is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BL8psxi6j6EKqPbLmibNfdTBGEzSopSbkNV4zTrZejP3iwB41NE is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMNuBhHneczA9SqXgtMeXTE1nGEEqrHTZDS6sFo4b4Y5ANtv5Py is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLJ8CgCem1RLtSx69Rc4nDoLSkgSvp8btAXavvByckWfsB8hMWu is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BMSTGM4x5JGMgUKRfoeoLhFNNjy8jRfHLDZcGABm6SNYzp4bLUc is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLECmtyz3w3ptsEjSBFaxUT6fTTTeJxdRJR1qyUHG6w7XGVoxNk is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BL3jWQTcR5iuVGy1d8Byems4qNDdw5XE9bASnp49FkeUXvcP4tV is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMeYvSdf5nb8ZMEjEpnHc8SDHLHwmUChqJBjmekqy4gEpmVou8A is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLnj2mCr53ntdKHaCF3pWEVqSpLiLRJMd2ztyR9ovSHAXjSEtQV is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BL9KfSyYMM3sXDNmfuwuR1sozNuGiAmyXuqFQJP4kzXJb65FQsW is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLRab5AzD7GX8726Fs8bwhwkuoFcMwEaBYQN7Yr28SAfwWZenBR is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMKLozJrePa48712zpctSZTpTFUbKjsgzDTpEZ2rRcvjUPRri5D is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BMUhGsiNLAeTSiU5eW4uZMFyvQ54XXyeWKAQ998iTgoVz2Fv4B8 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLwaC2bV4oURhUGR9b32izKbGBMdYPsKJ2W7kk7z5P6bpwmq8Dt is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BM9VN9mD44kAv6CZrBvYv55rYaxtXAKEKktN8Qb1S7bjN4tCKZY is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BM7xupqiUKogqpfbk1UudZmBN4xfkuaDLyLmPiM3o3HYSUF2B8d is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BL3s3rteYimQgmp8NdA8z49LXWNksnKNzwJBB7ZQdQVEpY5cE5e is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMPJgdCDVewUivbAzGqWbXiE1Lv5GHTktP12hbsZNZBrFRuvcrs is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BM4gUT4QbYKEbbeuLcKq5vCwRDAFduL9K2bCxtKx7oCbmr6rpyK is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMcmfgYcVRujvZrtw6qWdLaCxPra9XKUDFskiTxteajPBotuVsY is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLmbZ99TPQLjJM4RPTMxPDdjfXspncYLLLd1iYcrMktWpTxdb2Z is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLr943GR6m7mjEzNpQ9fmyWQk34Wqw5HSipg6xKfupULrUhWCMw is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMPY21UPKZfaxVJR2PEwbWTY3BGsKeQgkVj86c3Taz2fgZHJP6n is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMGYSvatadU3K8Xn7GKacaNUozjF3kgiwjBvnRWebhxzPUoT7kg is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLmvaxoZvWQ1F7hPmZ7RCqM5QMnBJVn29t16A98aefBaLaBaPWz is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLan1LFURPww5cP8CzHDuRRWC1Ec8HVhFpYp1JRY7QgwcVcprN2 is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BL3NZUvWePKiSdXRMvSuhTqHaQNwGjzqc2JmnRzmfxtqqm8dY9T is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BL2AWwV8qonvKxF4UGa3MJQrMGEG6efbfr7XJ7AVh1aTf2TYcfX is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BL1eU9563ccvPEdohmmrXLFPc8jyMEhJ7SwPUq6idnff856pV5S is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMLRyqzhPzSTLLVguf9RvhwQ3ZnSrc1MXsRMD3ERo1NZ4WrCKD3 is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLyFgygqX5Y6aHVUmusTJy3RgCjiZEfaKexvXW1Ndz7x9vUtU3r is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BMXohcYnwBhofBNToHZRUDWVumjBik5DEBmRxkkYEVSahkBheab is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLbkGg36mZMa6nNGtSHK55MMMVnBDq5U3nbWN1bGXePcCwwQSeX is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BMWj9u7fu4dKPkAuE2gq7dcK9Erwm2bpXUH2jdLNvXHoczZFCXH is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BKogWtiGoGsujKZw9qc6R8Wm7F4DU4EhbeP2BhP7UywsmAvkh3Y is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMY8aSrGs7oAdXFEmRCrcjBzHAeiUZLHneLh497xKRuMkHqq8w3 is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BKrWAxR2XCR3qwp6hVe7rNmNYaky8GrZQhd5puNXL4sJYSLK4mK is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLxtNLD3Qo3EJ2ZfadJ945unXZU8wod6bq6rw5T52ZTeYrWUDDp is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLUZVL241ofvM2CcXx1RVT7gPPWKzyVbC6qm6ELzT9nJdWWAmUj is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLgQYJFnzSfXeuhQ5x3FnaZwMMxSAfKhGh21AbeqY5nXhMPy1BG is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BL2Kq5FN8HqxBx1tT7ghati7k4CiKb8fXk5PTsSQWqgBJLThvkX is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLqGodNvCWaZgTXqMGxGYxmKbedLKn2axo1cHY753zo5Gxf5d33 is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLfWVKU9BaTDc6ih3CDpEXcfBnhF4ohfvWsQF6W5QdbjeXbHniX is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BL2MqE6uNouYEz3arMnNbBxPGeuM1zUVt3Xb1RBDHf76dC7pCFJ is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMVPYUHCctPj1JtPx9CVvLLSQ9atWkBpeuGSG7Fh2zWbmA42c4i is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BM76bidLLo6CZu6y852erVSV9Pf44zpFsk4iJoosLxpDSaENTCH is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BM7rgLH4CCLsrAEvhr8JNL3K9AvF2KuhifVPiZq2XZAg8VqAnMF is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLZkp6D7y4UYm5VuyrpvQo1tPAZLs8iw4wxASHJXoDV67rLJ36Z is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BM5zvxR4srvEtJhvD9S54qWvHywuRKPMFARvmahJqDZbfVsDE7V is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLaygV9bsByytQCV3aP4J1ARxmZ1z4afbmmChC3YWwZLGMWq3Ep is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLcrq7Kw5QayN2syao1HMKNGDMFyWL3pG8giHUKAm5kpwNyD5pT is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLPopch29iCxeKVZfo62aR4bJi4Py1AQ1QqbcwK69m7EV5ga27Y is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMZ2cQg63g2SWQijVwV3uyyzj1BUL2eAqDueZgUormonoXxkd2W is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMBxfJ46s7xiLfj6rGBqmtV8kjgJ9D1uALFLPcAZR4Hm3rXbP3j is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BKirGHqEKmrgKdB9fmc6Kd3SkLgCejGjnwgzLSuzUNXvYaeHdDJ is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLgiWmwqpnssFxBvH72tpjZbsYsbhh4DLfLh5vefAtSCKgfJGhB is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMUy5uhMfviFRDMmjx7Wx184ewGkGw22mBnVBHNtSUd6waV251P is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BLCtci1japxRQaH7g6mB7qj2DhKEjG1ZjNwY1HJhDDKxycY8BKu is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BM28jb2MnYSMY2xd1GCbSV19HWj3vqqkxzPotwuymzeXvh3nEfh is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLqBvygWoLAKeB75HF2evJstgDph7Nmjx2d5umRusum5DC8RYkc is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BMesvddj4WX7bbi7DBj9UZ2HD4BnR9uXFEjdNCwbTCvoVZV6py5 is finalized
INFO     pytezos:shell.py:100 Wait 1 seconds until block BKodxV7JhW2bUmzRahkcNLSDcFn2qxR3ffEDajWadaeMvGqwuHt is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLkjokoFfSbPWBiKcFLrKRqXBVcdBYE5iBge7iUGAy2gV6MD8DD is finalized
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLuBTfE8sZ3BNoFhMQhzfkEPoWwxv8K5SM83MNx3sDResmVLfFt is finalized
----------------------------- Captured stdout call -----------------------------
({'id': 'proto.008-PtEdo2Zk.michelson_v1.script_rejected',
  'kind': 'temporary',
  'location': 333,
  'with': {'string': 'Market auction closed'}},)
______________________ test_auction_clear[account1-data1] ______________________

transaction = <pytezos.operation.group.OperationGroup object at 0x7ff5ac369c40>

Properties
.key		tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNG...pply()
.proposals()
.result()
.reveal()
.run()
.run_operation()
.seed_nonce_revelation()
.send()
.sign()
.transaction()
count = None, tries = 3, error_func = <function print_error at 0x7ff5acdf7790>

    def submit_transaction(transaction, count=None, tries=3, error_func=None):
        """
        Submit a transaction
        """
        try:
            source = transaction.key.public_key_hash()
>           transaction_ = transaction.autofill(ttl=56)

src/utils.py:74: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <pytezos.operation.group.OperationGroup object at 0x7ff5ac369c40>

Properties
.key		tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNG...pply()
.proposals()
.result()
.reveal()
.run()
.run_operation()
.seed_nonce_revelation()
.send()
.sign()
.transaction()
gas_reserve = 100, burn_reserve = 100, counter = None, ttl = 56, fee = None
gas_limit = None, storage_limit = None, kwargs = {}
opg = <pytezos.operation.group.OperationGroup object at 0x7ff5ac7812b0>

Properties
.key		tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNG...pply()
.proposals()
.result()
.reveal()
.run()
.run_operation()
.seed_nonce_revelation()
.send()
.sign()
.transaction()
opg_with_metadata = {'contents': [{'amount': '0', 'counter': '68', 'destination': 'KT1W5yTZUT9rJYUCXRCHcY7Ko51D7Suf6PV9', 'fee': '104294', ...}], 'signature': 'sigUHx32f9wesZ1n2BWpixXz4AQaZggEtchaQNHYGRCoWNAXx45WGW2ua3apUUUAGMLPwAU41QoaFCzVSL61VaessLg4YbbP'}

    def autofill(
        self,
        gas_reserve: int = DEFAULT_GAS_RESERVE,
        burn_reserve: int = DEFAULT_BURN_RESERVE,
        counter: Optional[int] = None,
        ttl: Optional[int] = None,
        fee: Optional[int] = None,
        gas_limit: Optional[int] = None,
        storage_limit: Optional[int] = None,
        **kwargs
    ) -> 'OperationGroup':
        """Fill the gaps and then simulate the operation in order to calculate fee, gas/storage limits.
    
        :param gas_reserve: Add a safe reserve for dynamically calculated gas limit (default is 100).
        :param burn_reserve: Add a safe reserve for dynamically calculated storage limit (default is 100).
        :param counter: Override counter value (for manual handling)
        :param ttl: Number of blocks to wait in the mempool before removal (default is 5 for public network, 60 for sandbox)
        :param fee: Explicitly set fee for operation. If not set fee will be calculated depeding on results of operation dry-run.
        :param gas_limit: Explicitly set gas limit for operation. If not set gas limit will be calculated depeding on results of
            operation dry-run.
        :param storage_limit: Explicitly set storage limit for operation. If not set storage limit will be calculated depeding on
            results of operation dry-run.
        :rtype: OperationGroup
        """
        if kwargs.get('branch_offset') is not None:
            logger.warning('`branch_offset` argument is deprecated, use `ttl` instead')
            ttl = MAX_OPERATIONS_TTL - kwargs['branch_offset']
    
        opg = self.fill(counter=counter, ttl=ttl)
        opg_with_metadata = opg.run()
        if not OperationResult.is_applied(opg_with_metadata):
>           raise RpcError.from_errors(OperationResult.errors(opg_with_metadata))
E           pytezos.rpc.errors.MichelsonError: ({'id': 'proto.008-PtEdo2Zk.michelson_v1.script_rejected',
E             'kind': 'temporary',
E             'location': 333,
E             'with': {'string': 'Market auction closed'}},)

/home/killua/.cache/pypoetry/virtualenvs/prediction-market-support-mREyC6rD-py3.9/lib/python3.9/site-packages/pytezos/operation/group.py:228: MichelsonError

During handling of the above exception, another exception occurred:

account = {'key': 'tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3', 'name': 'mala'}
market = <src.market.Market object at 0x7ff5abdf1340>
data = ['who', 'why', 'mala', 300, 50000000, 76, ...]
questions_storage = <pytezos.contract.data.ContractData object at 0x7ff5ac52cc70>

Properties
.key		tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb
....tted datetime `%Y-%m-%dT%H:%M:%SZ` */


Helpers
.decode()
.default()
.dummy()
.encode()
.to_micheline()
.to_michelson()
gen_cleared_markets = [{'caller_name': 'palu', 'id': 5417074671350863707}, {'caller_name': 'marty', 'id': 4627002818767176605}, {'caller_nam...2939880851}, {'caller_name': 'palu', 'id': 284766939684584008}, {'caller_name': 'palu', 'id': 106130679728296059}, ...]

    @pytest.mark.parametrize("account,data", test_data)
    def test_auction_clear(account, market, data, questions_storage, gen_cleared_markets):
        auction = random.choice(gen_cleared_markets)
        amount = rand(100)
        rate = random.randint(0, 2 ** 63)
        transaction = market.auction_clear(auction['id'], auction["caller_name"])
>       submit_transaction(transaction, error_func=print_error)

tests/test_market.py:74: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/utils.py:80: in submit_transaction
    err_message = ast.literal_eval(str(r)[1-2])
/usr/lib/python3.9/ast.py:62: in literal_eval
    node_or_string = parse(node_or_string, mode='eval')
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

source = ')', filename = '<unknown>', mode = 'eval'

    def parse(source, filename='<unknown>', mode='exec', *,
              type_comments=False, feature_version=None):
        """
        Parse the source into an AST node.
        Equivalent to compile(source, filename, mode, PyCF_ONLY_AST).
        Pass type_comments=True to get back type comments where the syntax allows.
        """
        flags = PyCF_ONLY_AST
        if type_comments:
            flags |= PyCF_TYPE_COMMENTS
        if isinstance(feature_version, tuple):
            major, minor = feature_version  # Should be a 2-tuple.
            assert major == 3
            feature_version = minor
        elif feature_version is None:
            feature_version = -1
        # Else it should be an int giving the minor version for 3.x.
>       return compile(source, filename, mode, flags,
                       _feature_version=feature_version)
E         File "<unknown>", line 1
E           )
E           ^
E       SyntaxError: unmatched ')'

/usr/lib/python3.9/ast.py:50: SyntaxError
---------------------------- Captured stdout setup -----------------------------
mock_function
----------------------------- Captured stdout call -----------------------------
({'id': 'proto.008-PtEdo2Zk.michelson_v1.script_rejected',
  'kind': 'temporary',
  'location': 333,
  'with': {'string': 'Market auction closed'}},)
________________ test_market_enter_exist_payin[account0-data0] _________________

account = {'key': 'tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2', 'name': 'donald'}
market = <src.market.Market object at 0x7ff5abdf1340>
data = ['who', 'why', 'donald', 300000000, 122, 0.1]
liquidity_storage = <pytezos.contract.data.ContractData object at 0x7ff5ab4fc490>

Properties
.key		tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb
.... */

$nat:
	int  /* Natural number */


Helpers
.decode()
.default()
.dummy()
.encode()
.to_micheline()
.to_michelson()
gen_cleared_markets = [{'caller_name': 'palu', 'id': 5417074671350863707}, {'caller_name': 'marty', 'id': 4627002818767176605}, {'caller_nam...2939880851}, {'caller_name': 'palu', 'id': 284766939684584008}, {'caller_name': 'palu', 'id': 106130679728296059}, ...]

    @pytest.mark.parametrize("account,data", test_data)
    def test_market_enter_exist_payin(account, market, data, liquidity_storage, gen_cleared_markets):
        auction = random.choice(gen_cleared_markets)
        transaction = market.market_enter_exit(auction["id"], account['name'], 'payIn', 100)
        submit_transaction(transaction, error_func=print_error)
        sleep(3)
        key = {'originator': account['key'], 'market_id': auction['id']}
>       bids = liquidity_storage[key]

tests/test_market.py:120: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <pytezos.contract.data.ContractData object at 0x7ff5ab4fc490>

Properties
.key		tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb
.... */

$nat:
	int  /* Natural number */


Helpers
.decode()
.default()
.dummy()
.encode()
.to_micheline()
.to_michelson()
item = {'market_id': 4094108174030683379, 'originator': 'tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2'}

    def __getitem__(self, item: Union[str, int]) -> 'ContractData':
        """ Access child elements by name or index (depending on the type)
    
        :param item: field name (str) or index (int)
        :rtype: ContractData
        """
        res = self.data[item]
        if res is None:
>           raise KeyError(item)
E           KeyError: {'originator': 'tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2', 'market_id': 4094108174030683379}

/home/killua/.cache/pypoetry/virtualenvs/prediction-market-support-mREyC6rD-py3.9/lib/python3.9/site-packages/pytezos/contract/data.py:41: KeyError
---------------------------- Captured stdout setup -----------------------------
mock_function
----------------------------- Captured stdout call -----------------------------
Wait 0 seconds until block BLwc7VbY64qFxwN8XAkTi7wwfHYnKzMNb9iX9vrhbtiV2o8gWYY is finalized
------------------------------ Captured log call -------------------------------
INFO     pytezos:shell.py:100 Wait 0 seconds until block BLwc7VbY64qFxwN8XAkTi7wwfHYnKzMNb9iX9vrhbtiV2o8gWYY is finalized
________________ test_market_enter_exist_payin[account1-data1] _________________

account = {'key': 'tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3', 'name': 'mala'}
market = <src.market.Market object at 0x7ff5abdf1340>
data = ['who', 'why', 'mala', 300, 50000000, 76, ...]
liquidity_storage = <pytezos.contract.data.ContractData object at 0x7ff5ab4fc490>

Properties
.key		tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb
.... */

$nat:
	int  /* Natural number */


Helpers
.decode()
.default()
.dummy()
.encode()
.to_micheline()
.to_michelson()
gen_cleared_markets = [{'caller_name': 'palu', 'id': 5417074671350863707}, {'caller_name': 'marty', 'id': 4627002818767176605}, {'caller_nam...2939880851}, {'caller_name': 'palu', 'id': 284766939684584008}, {'caller_name': 'palu', 'id': 106130679728296059}, ...]

    @pytest.mark.parametrize("account,data", test_data)
    def test_market_enter_exist_payin(account, market, data, liquidity_storage, gen_cleared_markets):
        auction = random.choice(gen_cleared_markets)
        transaction = market.market_enter_exit(auction["id"], account['name'], 'payIn', 100)
        submit_transaction(transaction, error_func=print_error)
        sleep(3)
        key = {'originator': account['key'], 'market_id': auction['id']}
>       bids = liquidity_storage[key]

tests/test_market.py:120: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <pytezos.contract.data.ContractData object at 0x7ff5ab4fc490>

Properties
.key		tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb
.... */

$nat:
	int  /* Natural number */


Helpers
.decode()
.default()
.dummy()
.encode()
.to_micheline()
.to_michelson()
item = {'market_id': 6082298545284800581, 'originator': 'tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3'}

    def __getitem__(self, item: Union[str, int]) -> 'ContractData':
        """ Access child elements by name or index (depending on the type)
    
        :param item: field name (str) or index (int)
        :rtype: ContractData
        """
        res = self.data[item]
        if res is None:
>           raise KeyError(item)
E           KeyError: {'originator': 'tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3', 'market_id': 6082298545284800581}

/home/killua/.cache/pypoetry/virtualenvs/prediction-market-support-mREyC6rD-py3.9/lib/python3.9/site-packages/pytezos/contract/data.py:41: KeyError
---------------------------- Captured stdout setup -----------------------------
mock_function
----------------------------- Captured stdout call -----------------------------
Wait 0 seconds until block BKstvUypkYaX6WprMfLaUoA8DbRRT3iRkbUiYvBVJbVkmfKPq3Q is finalized
------------------------------ Captured log call -------------------------------
INFO     pytezos:shell.py:100 Wait 0 seconds until block BKstvUypkYaX6WprMfLaUoA8DbRRT3iRkbUiYvBVJbVkmfKPq3Q is finalized
_______________________ test_mint_token[account0-data0] ________________________

account = {'key': 'tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2', 'name': 'donald'}
market = <src.market.Market object at 0x7ff5abdf1340>
data = ['who', 'why', 'donald', 300000000, 122, 0.1]
supply_storage = <pytezos.contract.data.ContractData object at 0x7ff5ac6523a0>

Properties
.key		tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb
....
	}

$nat:
	int  /* Natural number */


Helpers
.decode()
.default()
.dummy()
.encode()
.to_micheline()
.to_michelson()
gen_cleared_markets = [{'caller_name': 'palu', 'id': 5417074671350863707}, {'caller_name': 'marty', 'id': 4627002818767176605}, {'caller_nam...2939880851}, {'caller_name': 'palu', 'id': 284766939684584008}, {'caller_name': 'palu', 'id': 106130679728296059}, ...]

    @pytest.mark.parametrize("account,data", test_data)
    def test_mint_token(account, market, data, supply_storage, gen_cleared_markets):
        auction = random.choice(gen_cleared_markets)
        amount = rand(100)
>       balance = supply_storage[(auction['id'] << 3) + 4]()

tests/test_market.py:129: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <pytezos.contract.data.ContractData object at 0x7ff5ac6523a0>

Properties
.key		tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb
....
	}

$nat:
	int  /* Natural number */


Helpers
.decode()
.default()
.dummy()
.encode()
.to_micheline()
.to_michelson()
item = 72330489008265094436

    def __getitem__(self, item: Union[str, int]) -> 'ContractData':
        """ Access child elements by name or index (depending on the type)
    
        :param item: field name (str) or index (int)
        :rtype: ContractData
        """
        res = self.data[item]
        if res is None:
>           raise KeyError(item)
E           KeyError: 72330489008265094436

/home/killua/.cache/pypoetry/virtualenvs/prediction-market-support-mREyC6rD-py3.9/lib/python3.9/site-packages/pytezos/contract/data.py:41: KeyError
---------------------------- Captured stdout setup -----------------------------
mock_function
_______________________ test_mint_token[account1-data1] ________________________

account = {'key': 'tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3', 'name': 'mala'}
market = <src.market.Market object at 0x7ff5abdf1340>
data = ['who', 'why', 'mala', 300, 50000000, 76, ...]
supply_storage = <pytezos.contract.data.ContractData object at 0x7ff5ac6523a0>

Properties
.key		tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb
....
	}

$nat:
	int  /* Natural number */


Helpers
.decode()
.default()
.dummy()
.encode()
.to_micheline()
.to_michelson()
gen_cleared_markets = [{'caller_name': 'palu', 'id': 5417074671350863707}, {'caller_name': 'marty', 'id': 4627002818767176605}, {'caller_nam...2939880851}, {'caller_name': 'palu', 'id': 284766939684584008}, {'caller_name': 'palu', 'id': 106130679728296059}, ...]

    @pytest.mark.parametrize("account,data", test_data)
    def test_mint_token(account, market, data, supply_storage, gen_cleared_markets):
        auction = random.choice(gen_cleared_markets)
        amount = rand(100)
>       balance = supply_storage[(auction['id'] << 3) + 4]()

tests/test_market.py:129: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <pytezos.contract.data.ContractData object at 0x7ff5ac6523a0>

Properties
.key		tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb
....
	}

$nat:
	int  /* Natural number */


Helpers
.decode()
.default()
.dummy()
.encode()
.to_micheline()
.to_michelson()
item = 64160763564058167028

    def __getitem__(self, item: Union[str, int]) -> 'ContractData':
        """ Access child elements by name or index (depending on the type)
    
        :param item: field name (str) or index (int)
        :rtype: ContractData
        """
        res = self.data[item]
        if res is None:
>           raise KeyError(item)
E           KeyError: 64160763564058167028

/home/killua/.cache/pypoetry/virtualenvs/prediction-market-support-mREyC6rD-py3.9/lib/python3.9/site-packages/pytezos/contract/data.py:41: KeyError
---------------------------- Captured stdout setup -----------------------------
mock_function
_______________________ test_burn_token[account0-data0] ________________________

account = {'key': 'tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2', 'name': 'donald'}
market = <src.market.Market object at 0x7ff5abdf1340>
data = ['who', 'why', 'donald', 300000000, 122, 0.1]
supply_storage = <pytezos.contract.data.ContractData object at 0x7ff5ac6523a0>

Properties
.key		tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb
....
	}

$nat:
	int  /* Natural number */


Helpers
.decode()
.default()
.dummy()
.encode()
.to_micheline()
.to_michelson()
gen_cleared_markets = [{'caller_name': 'palu', 'id': 5417074671350863707}, {'caller_name': 'marty', 'id': 4627002818767176605}, {'caller_nam...2939880851}, {'caller_name': 'palu', 'id': 284766939684584008}, {'caller_name': 'palu', 'id': 106130679728296059}, ...]

    @pytest.mark.parametrize("account,data", test_data)
    def test_burn_token(account, market, data, supply_storage, gen_cleared_markets):
        auction = random.choice(gen_cleared_markets)
>       balance = supply_storage[(auction['id'] << 3) + 4]()

tests/test_market.py:140: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <pytezos.contract.data.ContractData object at 0x7ff5ac6523a0>

Properties
.key		tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb
....
	}

$nat:
	int  /* Natural number */


Helpers
.decode()
.default()
.dummy()
.encode()
.to_micheline()
.to_michelson()
item = 47309963058938290284

    def __getitem__(self, item: Union[str, int]) -> 'ContractData':
        """ Access child elements by name or index (depending on the type)
    
        :param item: field name (str) or index (int)
        :rtype: ContractData
        """
        res = self.data[item]
        if res is None:
>           raise KeyError(item)
E           KeyError: 47309963058938290284

/home/killua/.cache/pypoetry/virtualenvs/prediction-market-support-mREyC6rD-py3.9/lib/python3.9/site-packages/pytezos/contract/data.py:41: KeyError
---------------------------- Captured stdout setup -----------------------------
mock_function
_______________________ test_burn_token[account1-data1] ________________________

account = {'key': 'tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3', 'name': 'mala'}
market = <src.market.Market object at 0x7ff5abdf1340>
data = ['who', 'why', 'mala', 300, 50000000, 76, ...]
supply_storage = <pytezos.contract.data.ContractData object at 0x7ff5ac6523a0>

Properties
.key		tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb
....
	}

$nat:
	int  /* Natural number */


Helpers
.decode()
.default()
.dummy()
.encode()
.to_micheline()
.to_michelson()
gen_cleared_markets = [{'caller_name': 'palu', 'id': 5417074671350863707}, {'caller_name': 'marty', 'id': 4627002818767176605}, {'caller_nam...2939880851}, {'caller_name': 'palu', 'id': 284766939684584008}, {'caller_name': 'palu', 'id': 106130679728296059}, ...]

    @pytest.mark.parametrize("account,data", test_data)
    def test_burn_token(account, market, data, supply_storage, gen_cleared_markets):
        auction = random.choice(gen_cleared_markets)
>       balance = supply_storage[(auction['id'] << 3) + 4]()

tests/test_market.py:140: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <pytezos.contract.data.ContractData object at 0x7ff5ac6523a0>

Properties
.key		tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb
....
	}

$nat:
	int  /* Natural number */


Helpers
.decode()
.default()
.dummy()
.encode()
.to_micheline()
.to_michelson()
item = 68648971602101815444

    def __getitem__(self, item: Union[str, int]) -> 'ContractData':
        """ Access child elements by name or index (depending on the type)
    
        :param item: field name (str) or index (int)
        :rtype: ContractData
        """
        res = self.data[item]
        if res is None:
>           raise KeyError(item)
E           KeyError: 68648971602101815444

/home/killua/.cache/pypoetry/virtualenvs/prediction-market-support-mREyC6rD-py3.9/lib/python3.9/site-packages/pytezos/contract/data.py:41: KeyError
---------------------------- Captured stdout setup -----------------------------
mock_function
_______________________ test_swap_tokens[account0-data0] _______________________

transaction = <pytezos.operation.group.OperationGroup object at 0x7ff5ac4c33d0>

Properties
.key		tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNG...pply()
.proposals()
.result()
.reveal()
.run()
.run_operation()
.seed_nonce_revelation()
.send()
.sign()
.transaction()
count = None, tries = 3, error_func = <function print_error at 0x7ff5acdf7790>

    def submit_transaction(transaction, count=None, tries=3, error_func=None):
        """
        Submit a transaction
        """
        try:
            source = transaction.key.public_key_hash()
>           transaction_ = transaction.autofill(ttl=56)

src/utils.py:74: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <pytezos.operation.group.OperationGroup object at 0x7ff5ac4c33d0>

Properties
.key		tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNG...pply()
.proposals()
.result()
.reveal()
.run()
.run_operation()
.seed_nonce_revelation()
.send()
.sign()
.transaction()
gas_reserve = 100, burn_reserve = 100, counter = None, ttl = 56, fee = None
gas_limit = None, storage_limit = None, kwargs = {}
opg = <pytezos.operation.group.OperationGroup object at 0x7ff5ac39c520>

Properties
.key		tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNG...pply()
.proposals()
.result()
.reveal()
.run()
.run_operation()
.seed_nonce_revelation()
.send()
.sign()
.transaction()
opg_with_metadata = {'contents': [{'amount': '0', 'counter': '70', 'destination': 'KT1W5yTZUT9rJYUCXRCHcY7Ko51D7Suf6PV9', 'fee': '104302', ...}], 'signature': 'sigUHx32f9wesZ1n2BWpixXz4AQaZggEtchaQNHYGRCoWNAXx45WGW2ua3apUUUAGMLPwAU41QoaFCzVSL61VaessLg4YbbP'}

    def autofill(
        self,
        gas_reserve: int = DEFAULT_GAS_RESERVE,
        burn_reserve: int = DEFAULT_BURN_RESERVE,
        counter: Optional[int] = None,
        ttl: Optional[int] = None,
        fee: Optional[int] = None,
        gas_limit: Optional[int] = None,
        storage_limit: Optional[int] = None,
        **kwargs
    ) -> 'OperationGroup':
        """Fill the gaps and then simulate the operation in order to calculate fee, gas/storage limits.
    
        :param gas_reserve: Add a safe reserve for dynamically calculated gas limit (default is 100).
        :param burn_reserve: Add a safe reserve for dynamically calculated storage limit (default is 100).
        :param counter: Override counter value (for manual handling)
        :param ttl: Number of blocks to wait in the mempool before removal (default is 5 for public network, 60 for sandbox)
        :param fee: Explicitly set fee for operation. If not set fee will be calculated depeding on results of operation dry-run.
        :param gas_limit: Explicitly set gas limit for operation. If not set gas limit will be calculated depeding on results of
            operation dry-run.
        :param storage_limit: Explicitly set storage limit for operation. If not set storage limit will be calculated depeding on
            results of operation dry-run.
        :rtype: OperationGroup
        """
        if kwargs.get('branch_offset') is not None:
            logger.warning('`branch_offset` argument is deprecated, use `ttl` instead')
            ttl = MAX_OPERATIONS_TTL - kwargs['branch_offset']
    
        opg = self.fill(counter=counter, ttl=ttl)
        opg_with_metadata = opg.run()
        if not OperationResult.is_applied(opg_with_metadata):
>           raise RpcError.from_errors(OperationResult.errors(opg_with_metadata))
E           pytezos.rpc.errors.MichelsonError: ({'id': 'proto.008-PtEdo2Zk.michelson_v1.script_rejected',
E             'kind': 'temporary',
E             'location': 143,
E             'with': {'string': 'Not enough balance in source account'}},)

/home/killua/.cache/pypoetry/virtualenvs/prediction-market-support-mREyC6rD-py3.9/lib/python3.9/site-packages/pytezos/operation/group.py:228: MichelsonError

During handling of the above exception, another exception occurred:

account = {'key': 'tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2', 'name': 'donald'}
market = <src.market.Market object at 0x7ff5abdf1340>
data = ['who', 'why', 'donald', 300000000, 122, 0.1]
supply_storage = <pytezos.contract.data.ContractData object at 0x7ff5ac6523a0>

Properties
.key		tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb
....
	}

$nat:
	int  /* Natural number */


Helpers
.decode()
.default()
.dummy()
.encode()
.to_micheline()
.to_michelson()
gen_cleared_markets = [{'caller_name': 'palu', 'id': 5417074671350863707}, {'caller_name': 'marty', 'id': 4627002818767176605}, {'caller_nam...2939880851}, {'caller_name': 'palu', 'id': 284766939684584008}, {'caller_name': 'palu', 'id': 106130679728296059}, ...]

    @pytest.mark.parametrize("account,data", test_data)
    def test_swap_tokens(account, market, data, supply_storage, gen_cleared_markets):
        auction = random.choice(gen_cleared_markets)
        balance = supply_storage[(auction['id'] << 3) + 1]()
        transaction = market.swap_tokens(auction['id'], account["name"], "yes", 150)
>       submit_transaction(transaction, error_func=print_error)

tests/test_market.py:154: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/utils.py:80: in submit_transaction
    err_message = ast.literal_eval(str(r)[1-2])
/usr/lib/python3.9/ast.py:62: in literal_eval
    node_or_string = parse(node_or_string, mode='eval')
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

source = ')', filename = '<unknown>', mode = 'eval'

    def parse(source, filename='<unknown>', mode='exec', *,
              type_comments=False, feature_version=None):
        """
        Parse the source into an AST node.
        Equivalent to compile(source, filename, mode, PyCF_ONLY_AST).
        Pass type_comments=True to get back type comments where the syntax allows.
        """
        flags = PyCF_ONLY_AST
        if type_comments:
            flags |= PyCF_TYPE_COMMENTS
        if isinstance(feature_version, tuple):
            major, minor = feature_version  # Should be a 2-tuple.
            assert major == 3
            feature_version = minor
        elif feature_version is None:
            feature_version = -1
        # Else it should be an int giving the minor version for 3.x.
>       return compile(source, filename, mode, flags,
                       _feature_version=feature_version)
E         File "<unknown>", line 1
E           )
E           ^
E       SyntaxError: unmatched ')'

/usr/lib/python3.9/ast.py:50: SyntaxError
---------------------------- Captured stdout setup -----------------------------
mock_function
----------------------------- Captured stdout call -----------------------------
({'id': 'proto.008-PtEdo2Zk.michelson_v1.script_rejected',
  'kind': 'temporary',
  'location': 143,
  'with': {'string': 'Not enough balance in source account'}},)
_______________________ test_swap_tokens[account1-data1] _______________________

transaction = <pytezos.operation.group.OperationGroup object at 0x7ff5ac5c7d90>

Properties
.key		tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5y...pply()
.proposals()
.result()
.reveal()
.run()
.run_operation()
.seed_nonce_revelation()
.send()
.sign()
.transaction()
count = None, tries = 3, error_func = <function print_error at 0x7ff5acdf7790>

    def submit_transaction(transaction, count=None, tries=3, error_func=None):
        """
        Submit a transaction
        """
        try:
            source = transaction.key.public_key_hash()
>           transaction_ = transaction.autofill(ttl=56)

src/utils.py:74: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <pytezos.operation.group.OperationGroup object at 0x7ff5ac5c7d90>

Properties
.key		tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5y...pply()
.proposals()
.result()
.reveal()
.run()
.run_operation()
.seed_nonce_revelation()
.send()
.sign()
.transaction()
gas_reserve = 100, burn_reserve = 100, counter = None, ttl = 56, fee = None
gas_limit = None, storage_limit = None, kwargs = {}
opg = <pytezos.operation.group.OperationGroup object at 0x7ff5ac308a90>

Properties
.key		tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5y...pply()
.proposals()
.result()
.reveal()
.run()
.run_operation()
.seed_nonce_revelation()
.send()
.sign()
.transaction()
opg_with_metadata = {'contents': [{'amount': '0', 'counter': '69', 'destination': 'KT1W5yTZUT9rJYUCXRCHcY7Ko51D7Suf6PV9', 'fee': '104303', ...}], 'signature': 'sigUHx32f9wesZ1n2BWpixXz4AQaZggEtchaQNHYGRCoWNAXx45WGW2ua3apUUUAGMLPwAU41QoaFCzVSL61VaessLg4YbbP'}

    def autofill(
        self,
        gas_reserve: int = DEFAULT_GAS_RESERVE,
        burn_reserve: int = DEFAULT_BURN_RESERVE,
        counter: Optional[int] = None,
        ttl: Optional[int] = None,
        fee: Optional[int] = None,
        gas_limit: Optional[int] = None,
        storage_limit: Optional[int] = None,
        **kwargs
    ) -> 'OperationGroup':
        """Fill the gaps and then simulate the operation in order to calculate fee, gas/storage limits.
    
        :param gas_reserve: Add a safe reserve for dynamically calculated gas limit (default is 100).
        :param burn_reserve: Add a safe reserve for dynamically calculated storage limit (default is 100).
        :param counter: Override counter value (for manual handling)
        :param ttl: Number of blocks to wait in the mempool before removal (default is 5 for public network, 60 for sandbox)
        :param fee: Explicitly set fee for operation. If not set fee will be calculated depeding on results of operation dry-run.
        :param gas_limit: Explicitly set gas limit for operation. If not set gas limit will be calculated depeding on results of
            operation dry-run.
        :param storage_limit: Explicitly set storage limit for operation. If not set storage limit will be calculated depeding on
            results of operation dry-run.
        :rtype: OperationGroup
        """
        if kwargs.get('branch_offset') is not None:
            logger.warning('`branch_offset` argument is deprecated, use `ttl` instead')
            ttl = MAX_OPERATIONS_TTL - kwargs['branch_offset']
    
        opg = self.fill(counter=counter, ttl=ttl)
        opg_with_metadata = opg.run()
        if not OperationResult.is_applied(opg_with_metadata):
>           raise RpcError.from_errors(OperationResult.errors(opg_with_metadata))
E           pytezos.rpc.errors.MichelsonError: ({'id': 'proto.008-PtEdo2Zk.michelson_v1.script_rejected',
E             'kind': 'temporary',
E             'location': 143,
E             'with': {'string': 'Not enough balance in source account'}},)

/home/killua/.cache/pypoetry/virtualenvs/prediction-market-support-mREyC6rD-py3.9/lib/python3.9/site-packages/pytezos/operation/group.py:228: MichelsonError

During handling of the above exception, another exception occurred:

account = {'key': 'tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3', 'name': 'mala'}
market = <src.market.Market object at 0x7ff5abdf1340>
data = ['who', 'why', 'mala', 300, 50000000, 76, ...]
supply_storage = <pytezos.contract.data.ContractData object at 0x7ff5ac6523a0>

Properties
.key		tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb
....
	}

$nat:
	int  /* Natural number */


Helpers
.decode()
.default()
.dummy()
.encode()
.to_micheline()
.to_michelson()
gen_cleared_markets = [{'caller_name': 'palu', 'id': 5417074671350863707}, {'caller_name': 'marty', 'id': 4627002818767176605}, {'caller_nam...2939880851}, {'caller_name': 'palu', 'id': 284766939684584008}, {'caller_name': 'palu', 'id': 106130679728296059}, ...]

    @pytest.mark.parametrize("account,data", test_data)
    def test_swap_tokens(account, market, data, supply_storage, gen_cleared_markets):
        auction = random.choice(gen_cleared_markets)
        balance = supply_storage[(auction['id'] << 3) + 1]()
        transaction = market.swap_tokens(auction['id'], account["name"], "yes", 150)
>       submit_transaction(transaction, error_func=print_error)

tests/test_market.py:154: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/utils.py:80: in submit_transaction
    err_message = ast.literal_eval(str(r)[1-2])
/usr/lib/python3.9/ast.py:62: in literal_eval
    node_or_string = parse(node_or_string, mode='eval')
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

source = ')', filename = '<unknown>', mode = 'eval'

    def parse(source, filename='<unknown>', mode='exec', *,
              type_comments=False, feature_version=None):
        """
        Parse the source into an AST node.
        Equivalent to compile(source, filename, mode, PyCF_ONLY_AST).
        Pass type_comments=True to get back type comments where the syntax allows.
        """
        flags = PyCF_ONLY_AST
        if type_comments:
            flags |= PyCF_TYPE_COMMENTS
        if isinstance(feature_version, tuple):
            major, minor = feature_version  # Should be a 2-tuple.
            assert major == 3
            feature_version = minor
        elif feature_version is None:
            feature_version = -1
        # Else it should be an int giving the minor version for 3.x.
>       return compile(source, filename, mode, flags,
                       _feature_version=feature_version)
E         File "<unknown>", line 1
E           )
E           ^
E       SyntaxError: unmatched ')'

/usr/lib/python3.9/ast.py:50: SyntaxError
---------------------------- Captured stdout setup -----------------------------
mock_function
----------------------------- Captured stdout call -----------------------------
({'id': 'proto.008-PtEdo2Zk.michelson_v1.script_rejected',
  'kind': 'temporary',
  'location': 143,
  'with': {'string': 'Not enough balance in source account'}},)
=============================== warnings summary ===============================
../../../../../.cache/pypoetry/virtualenvs/prediction-market-support-mREyC6rD-py3.9/lib/python3.9/site-packages/cytoolz/compatibility.py:2
  /home/killua/.cache/pypoetry/virtualenvs/prediction-market-support-mREyC6rD-py3.9/lib/python3.9/site-packages/cytoolz/compatibility.py:2: DeprecationWarning: The toolz.compatibility module is no longer needed in Python 3 and has been deprecated. Please import these utilities directly from the standard library. This module will be removed in a future release.
    warnings.warn("The toolz.compatibility module is no longer "

-- Docs: https://docs.pytest.org/en/stable/warnings.html
=========================== short test summary info ============================
FAILED tests/test_market.py::test_ask_question[account1-data1] - assert 16208...
FAILED tests/test_market.py::test_auction_clear[account0-data0] -   File "<un...
FAILED tests/test_market.py::test_auction_clear[account1-data1] -   File "<un...
FAILED tests/test_market.py::test_market_enter_exist_payin[account0-data0] - ...
FAILED tests/test_market.py::test_market_enter_exist_payin[account1-data1] - ...
FAILED tests/test_market.py::test_mint_token[account0-data0] - KeyError: 7233...
FAILED tests/test_market.py::test_mint_token[account1-data1] - KeyError: 6416...
FAILED tests/test_market.py::test_burn_token[account0-data0] - KeyError: 4730...
FAILED tests/test_market.py::test_burn_token[account1-data1] - KeyError: 6864...
FAILED tests/test_market.py::test_swap_tokens[account0-data0] -   File "<unkn...
FAILED tests/test_market.py::test_swap_tokens[account1-data1] -   File "<unkn...
============ 11 failed, 29 passed, 1 warning in 10479.19s (2:54:39) ============
