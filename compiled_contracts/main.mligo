    m4_loadfile(.,storage.mligo.m4) m4_loadfile(.,installer.mligo.m4) m4_loadfile(.,lazy_endpoint_helper.mligo.m4) 
type market_action =
	| MarketCreate of create_market_params
	| AuctionBet of bet_params
	| AuctionClear of market_id
	| AuctionWithdraw of market_id
	| MarketEnterExit of directional_params
	| SwapTokens of token_trade_params
	| SwapLiquidity of directional_params
	| MarketResolve of resolve_market_params
	| ClaimWinnings of market_id

type main_action =
	| Installer of installer_action
	| Market of market_action

let market_dispatcher ( action, container_storage : market_action * container_storage ) : operation list * container_storage =
	match action with
	| MarketCreate params -> business_endpoint_dispatch ( "market_create_endpoint", Bytes.pack params, container_storage )
	| AuctionBet params -> business_endpoint_dispatch ( "auction_bet_endpoint", Bytes.pack params, container_storage )
	| AuctionClear params -> business_endpoint_dispatch ( "auction_clear_endpoint", Bytes.pack params, container_storage )
	| AuctionWithdraw params -> business_endpoint_dispatch ( "auction_withdraw_endpoint", Bytes.pack params, container_storage )
	| MarketEnterExit params -> business_endpoint_dispatch ( "market_enter_exit_endpoint", Bytes.pack params, container_storage )
	| SwapTokens params -> business_endpoint_dispatch ( "swap_swap_tokens_endpoint", Bytes.pack params, container_storage )
	| SwapLiquidity params -> business_endpoint_dispatch ( "swap_move_lqt_endpoint", Bytes.pack params, container_storage )
	| MarketResolve params -> business_endpoint_dispatch ( "market_resolve_endpoint", Bytes.pack params, container_storage )
	| ClaimWinnings params -> business_endpoint_dispatch ( "market_claim_endpoint", Bytes.pack params, container_storage )

let main ( action, container_storage : main_action * container_storage) : operation list * container_storage =
	match action with
	| Installer params -> installer_dispatch ( params, container_storage )
	| Market params -> market_dispatcher ( params, container_storage )

 