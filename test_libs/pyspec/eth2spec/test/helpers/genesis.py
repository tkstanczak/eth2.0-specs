# Access constants from spec pkg reference.
import eth2spec.phase0.spec as spec

from eth2spec.phase0.spec import Eth1Data, ZERO_HASH, get_active_validator_indices
from eth2spec.test.helpers.keys import pubkeys
from eth2spec.utils.minimal_ssz import hash_tree_root


def build_mock_validator(i: int, balance: int):
    pubkey = pubkeys[i]
    # insecurely use pubkey as withdrawal key as well
    withdrawal_credentials = spec.BLS_WITHDRAWAL_PREFIX_BYTE + spec.hash(pubkey)[1:]
    return spec.Validator(
        pubkey=pubkeys[i],
        withdrawal_credentials=withdrawal_credentials,
        activation_eligibility_epoch=spec.FAR_FUTURE_EPOCH,
        activation_epoch=spec.FAR_FUTURE_EPOCH,
        exit_epoch=spec.FAR_FUTURE_EPOCH,
        withdrawable_epoch=spec.FAR_FUTURE_EPOCH,
        effective_balance=min(balance - balance % spec.EFFECTIVE_BALANCE_INCREMENT, spec.MAX_EFFECTIVE_BALANCE)
    )


def create_genesis_state(num_validators):
    deposit_root = b'\x42' * 32

    state = spec.BeaconState(
        genesis_time=0,
        deposit_index=num_validators,
        latest_eth1_data=Eth1Data(
            deposit_root=deposit_root,
            deposit_count=num_validators,
            block_hash=ZERO_HASH,
        ))

    # We "hack" in the initial validators,
    #  as it is much faster than creating and processing genesis deposits for every single test case.
    state.balances = [spec.MAX_EFFECTIVE_BALANCE] * num_validators
    state.validator_registry = [build_mock_validator(i, state.balances[i]) for i in range(num_validators)]

    # Process genesis activations
    for validator in state.validator_registry:
        if validator.effective_balance >= spec.MAX_EFFECTIVE_BALANCE:
            validator.activation_eligibility_epoch = spec.GENESIS_EPOCH
            validator.activation_epoch = spec.GENESIS_EPOCH

    genesis_active_index_root = hash_tree_root(get_active_validator_indices(state, spec.GENESIS_EPOCH))
    for index in range(spec.LATEST_ACTIVE_INDEX_ROOTS_LENGTH):
        state.latest_active_index_roots[index] = genesis_active_index_root

    return state
