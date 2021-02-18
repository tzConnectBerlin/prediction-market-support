(*
 * Simple oracle contract.
 * The identifier for an oracle is an IPFS hash which should contain the following
 * fields:
 * question : the query to send to Wolfram Alpha
 * yes_answer : the response which will cause a yes to be emitted back to the calling contract.
 *
 * The 'owner' field is the only address allowed to answer queries.
 *
 * Error codes returned are:
 * 1 : Hash already present
 * 2 : Answer called by someone other than owner
 * 3 : Question not found
 * 4 : answer_at time not reached
 * 5 : Could not invoke answer operation on caller
 *
 *)
type callback_params = (string * bool)
type callback = CloseMarket of callback_params

type query_storage =
[@layout:comb]
{
    answer_to : address;
    question_id : string;
    answer_at : timestamp;
}

type storage =
[@layout:comb]
{
    questions : (string, query_storage) map;
    owner : address;
}

type parameter =
  | Ask of (string * timestamp * string)
  | Answer of (string * bool)

let ask (ipfs_hash, answer_at, question_id, storage : string * timestamp * string * storage) :
      operation list * storage =
  let x = match Map.find_opt ipfs_hash storage.questions with
    | Some x -> failwith "1"
    | None -> unit in
  let query : query_storage = { answer_to = Tezos.sender;
                                answer_at = answer_at;
                                question_id = question_id } in
  ([] : operation list), { storage with questions = Map.update ipfs_hash
                                                      (Some query ) storage.questions }

let answer (ipfs_hash, answer, storage : string * bool * storage) : operation list * storage =
  let x = if Tezos.sender <> storage.owner then failwith "2" else unit in
  let query : query_storage = match Map.find_opt ipfs_hash storage.questions with
    | Some x -> x
    | None -> (failwith "3" : query_storage) in
  let x = if Tezos.now < query.answer_at then failwith "4" else unit in
  let contract_to_answer : callback contract =
    match ((Tezos.get_entrypoint_opt "%closeMarket" query.answer_to) : callback contract option) with
    | Some c -> c
    | None -> (failwith "5" : callback contract) in
  let operation = Tezos.transaction (CloseMarket (query.question_id, answer)) 0tz contract_to_answer in
  ([operation] : operation list),
  { storage with questions = Map.remove ipfs_hash storage.questions }

let main (action, storage : parameter * storage) : operation list * storage =
  match action with
  | Ask params -> let (ipfs_hash, answer_at, question_id) = params in
                  ask (ipfs_hash, answer_at, question_id, storage)
  | Answer params -> let (ipfs_hash, answer_) = params in
                     answer (ipfs_hash, answer_, storage)
