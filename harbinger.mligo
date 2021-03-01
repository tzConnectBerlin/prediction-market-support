(*
 * Simple oracle contract.
 * The identifier for an oracle is an IPFS hash which should contain the following
 * fields:
 * question : the query to send to Wolfram Alpha
 * yes_answer : the response which will cause a yes to be emitted back to the calling contract.
 *
 * The 'owner' field is currently not used.
 *
 * Error codes returned are:
 * 1 : Hash already present
 * 2 : Answer called by someone other than owner
 * 3 : Question not found
 * 4 : answer_at time not reached
 * 5 : Could not invoke answer operation on caller
 * 6 : No current question
 *)
type query_storage =
[@layout:comb]
{
    answer_to : address;
    question_id : string;
    currency_pair : string;
    value : nat;
    answer_at : timestamp;
}

type storage =
[@layout:comb]
{
    current_question : string option;
    questions : (string, query_storage) map;
    owner : address;
    oracle : address;
  }

type callback_data =
[@layout:comb]
{
  currency_pair : string;
  last_update : timestamp;
  rate : nat;
}

type ask_params =
[@layout:comb]
{
  ipfs_hash : string;
  question_id : string;
  currency_pair : string;
  value : nat;
  answer_at : timestamp;
}

type harbinger_param = string * callback_data contract

type market_callback_params = (string * bool)
type market_callback = CloseMarket of market_callback_params

type parameter =
  | Ask of ask_params
  | Answer of string
  | Answer_callback of callback_data
  | Check_answered of unit

(*
Stores a question in the contract.
Fails if ipfs_hash is already a key

*)
let ask (params, storage : ask_params * storage) :
      operation list * storage =
  let x = match Map.find_opt params.ipfs_hash storage.questions with
    | Some x -> failwith "1"
    | None -> unit in
  let query : query_storage = { answer_to = Tezos.sender;
                                question_id = params.question_id;
                                currency_pair = params.currency_pair;
                                value = params.value;
                                answer_at = params.answer_at;
                              } in
  ([] : operation list),
  { storage with questions = Map.update params.ipfs_hash
                     (Some query ) storage.questions }

(*
Entrypoint which sets off a chain of events which may close a market.
ipfs_hash passed in, and query retrived (or failwith)
Checks the query is ready to be answered, else fail
Sets the current_question in storage to be ipfs_hash
Returns new storage and a list of 2 operations:
- the call to the oracle, which should result in a callback to this contract, and
- a check entrypoint, which ensures that the callback has been called.
*)
let answer (ipfs_hash, storage : string * storage) : operation list * storage =
  let query : query_storage = match Map.find_opt ipfs_hash storage.questions with
    | Some x -> x
    | None -> (failwith "3" : query_storage) in
  let x = if Tezos.now < query.answer_at then failwith "4" else unit in
  let harbinger : harbinger_param contract =
    match ((Tezos.get_entrypoint_opt "%get" storage.oracle) : harbinger_param contract option) with
    | Some c -> c
    | None -> (failwith "5" : harbinger_param contract) in
  let operation = Tezos.transaction
      (query.currency_pair, (Tezos.self("%answer_callback") : callback_data contract)) 0tz harbinger in
  let me : unit contract =
    match((Tezos.get_entrypoint_opt "%check_answered" Tezos.self_address) : unit contract option) with
    | Some c -> c
    | None -> (failwith "6" : unit contract) in
  let check_operation = Tezos.transaction () 0tz me in
  ([operation; check_operation] : operation list),
  { storage with questions = Map.remove ipfs_hash storage.questions;  current_question = Some(ipfs_hash) }

(*
Called by oracle. Requires that the caller is the oracle contract, and the current_question is not None.
Checks now is later than query.answer_at
Compares oracle_response.rate with query.value, calls closeMarket in PM contract with
 true if greater than, else false
Sets current_question to None and removes this question from the storage
*)
let answer_callback (params, storage : callback_data * storage) : operation list * storage =
  let x = if Tezos.sender <> storage.oracle then failwith "2" else unit in
  let ipfs_hash = match storage.current_question with
    | Some x -> x
    | None -> (failwith "6" : string) in
  let query : query_storage = match Map.find_opt ipfs_hash storage.questions with
    | Some x -> x
    | None -> (failwith "3" : query_storage) in
  let x = if Tezos.now < query.answer_at then failwith "4" else unit in
  let contract_to_answer : market_callback contract =
    match ((Tezos.get_entrypoint_opt "%closeMarket" query.answer_to) : market_callback contract option) with
    | Some c -> c
    | None -> (failwith "5" : market_callback contract) in
  let answer = if query.value > params.rate then true else false in
  let operation = Tezos.transaction (CloseMarket (query.question_id, answer)) 0tz contract_to_answer in
  ([operation] : operation list),
  { storage with questions = Map.remove ipfs_hash storage.questions;
                 current_question = (None : string option) }
(*
Last transaction executed. Checks that the oracle has called answer_callback, and question is now None.
If this is not the case, calls failwith to roll everything back.
*)
let check_answered (storage : storage) : storage =
  let x = match storage.current_question with
  | Some x -> failwith "7"
  | None -> unit in
  storage

let main (action, storage : parameter * storage) : operation list * storage =
  match action with
  | Ask params -> ask (params, storage)
  | Answer ipfs_hash -> answer (ipfs_hash, storage)
  | Answer_callback params -> answer_callback (params, storage)
  | Check_answered -> (([] : operation list), (check_answered storage))
