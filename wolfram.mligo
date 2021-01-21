type callback_params = (string * bool)
type callback = SubmitAnswer of callback_params

type query_storage = {
    answer_to : address;
    question_id : string;
    answer_at : timestamp;
    answered : bool
  }

type storage = {
    questions : (string, query_storage) big_map;
    owner : address;
  }

type parameter =
  | Ask of (string * timestamp * string)
  | Answer of (string * bool)

let ask (ipfs_hash, answer_at, question_id, storage : string * timestamp * string * storage) :
      operation list * storage =
  let x = match Big_map.find_opt ipfs_hash storage.questions with
    | Some x -> failwith "Hash already present"
    | None -> unit in
  let query : query_storage = { answer_to = Tezos.sender;
                                answer_at = answer_at;
                                answered = false;
                                question_id = question_id } in
  ([] : operation list), { storage with questions = Big_map.update ipfs_hash
                                                      (Some query ) storage.questions }

let answer (ipfs_hash, answer, storage : string * bool * storage) : operation list * storage =
  let x = if Tezos.sender <> storage.owner then failwith "Not authorized" else unit in
  let query : query_storage = match Big_map.find_opt ipfs_hash storage.questions with
    | Some x -> x
    | None -> (failwith "Query not found" : query_storage) in
  (* omitted test for already answered question. TODO: put this in *)
  (* omitted test for answer_at. TODO: put this in *)
  let contract_to_answer : callback contract =
    match ((Tezos.get_entrypoint_opt "%SubmitAnswer" query.answer_to) : callback contract option) with
    | Some c -> c
    | None -> (failwith "answer_to contract does not support method" : callback contract) in
  let operation = Tezos.transaction (SubmitAnswer (query.question_id, answer)) 0tz contract_to_answer in
  ([operation] : operation list), { storage with questions = Big_map.update ipfs_hash
                                                    (Some {query with answered = true })
                                                    storage.questions }

let main (action, storage : parameter * storage) : operation list * storage =
  match action with
  | Ask params -> let (ipfs_hash, answer_at, question_id) = params in
                  ask (ipfs_hash, answer_at, question_id, storage)
  | Answer params -> let (ipfs_hash, answer_) = params in
                     answer (ipfs_hash, answer_, storage)
