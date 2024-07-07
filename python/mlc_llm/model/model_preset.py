"""A builtin set of models available in MLC LLM."""

from typing import Any, Dict  # pylint: disable=too-many-lines

MODEL_PRESETS: Dict[str, Any] = {
    "llama2_7b": {
        "architectures": ["LlamaForCausalLM"],
        "bos_token_id": 1,
        "eos_token_id": 2,
        "hidden_act": "silu",
        "hidden_size": 4096,
        "initializer_range": 0.02,
        "intermediate_size": 11008,
        "max_position_embeddings": 2048,
        "model_type": "llama",
        "num_attention_heads": 32,
        "num_hidden_layers": 32,
        "num_key_value_heads": 32,
        "pad_token_id": 0,
        "pretraining_tp": 1,
        "rms_norm_eps": 1e-05,
        "rope_scaling": None,
        "tie_word_embeddings": False,
        "torch_dtype": "float16",
        "transformers_version": "4.31.0.dev0",
        "use_cache": True,
        "vocab_size": 32000,
        "context_window_size": 2048,
        "prefill_chunk_size": 2048,
    },
    "llama2_13b": {
        "_name_or_path": "meta-llama/Llama-2-13b-hf",
        "architectures": ["LlamaForCausalLM"],
        "bos_token_id": 1,
        "eos_token_id": 2,
        "hidden_act": "silu",
        "hidden_size": 5120,
        "initializer_range": 0.02,
        "intermediate_size": 13824,
        "max_position_embeddings": 2048,
        "model_type": "llama",
        "num_attention_heads": 40,
        "num_hidden_layers": 40,
        "num_key_value_heads": 40,
        "pad_token_id": 0,
        "pretraining_tp": 2,
        "rms_norm_eps": 1e-05,
        "rope_scaling": None,
        "tie_word_embeddings": False,
        "torch_dtype": "float16",
        "transformers_version": "4.31.0.dev0",
        "use_cache": True,
        "vocab_size": 32000,
        "context_window_size": 2048,
        "prefill_chunk_size": 2048,
    },
    "llama2_70b": {
        "architectures": ["LlamaForCausalLM"],
        "bos_token_id": 1,
        "eos_token_id": 2,
        "hidden_act": "silu",
        "hidden_size": 8192,
        "initializer_range": 0.02,
        "intermediate_size": 28672,
        "max_position_embeddings": 2048,
        "model_type": "llama",
        "num_attention_heads": 64,
        "num_hidden_layers": 80,
        "num_key_value_heads": 8,
        "pad_token_id": 0,
        "rms_norm_eps": 1e-05,
        "tie_word_embeddings": False,
        "torch_dtype": "float16",
        "transformers_version": "4.31.0.dev0",
        "use_cache": True,
        "vocab_size": 32000,
        "context_window_size": 2048,
        "prefill_chunk_size": 2048,
    },
    "codellama_7b": {
        "_name_or_path": "codellama/CodeLlama-7b-hf",
        "architectures": ["LlamaForCausalLM"],
        "bos_token_id": 1,
        "eos_token_id": 2,
        "hidden_act": "silu",
        "hidden_size": 4096,
        "initializer_range": 0.02,
        "intermediate_size": 11008,
        "max_position_embeddings": 16384,
        "model_type": "llama",
        "num_attention_heads": 32,
        "num_hidden_layers": 32,
        "num_key_value_heads": 32,
        "pretraining_tp": 1,
        "rms_norm_eps": 1e-05,
        "rope_scaling": None,
        "rope_theta": 1000000,
        "tie_word_embeddings": False,
        "torch_dtype": "bfloat16",
        "transformers_version": "4.33.0.dev0",
        "use_cache": True,
        "vocab_size": 32016,
        "context_window_size": 2048,
        "prefill_chunk_size": 2048,
    },
    "codellama_13b": {
        "architectures": ["LlamaForCausalLM"],
        "bos_token_id": 1,
        "eos_token_id": 2,
        "hidden_act": "silu",
        "hidden_size": 5120,
        "initializer_range": 0.02,
        "intermediate_size": 13824,
        "max_position_embeddings": 16384,
        "model_type": "llama",
        "num_attention_heads": 40,
        "num_hidden_layers": 40,
        "num_key_value_heads": 40,
        "pretraining_tp": 1,
        "rms_norm_eps": 1e-05,
        "rope_scaling": None,
        "rope_theta": 1000000,
        "tie_word_embeddings": False,
        "torch_dtype": "bfloat16",
        "transformers_version": "4.32.0.dev0",
        "use_cache": True,
        "vocab_size": 32016,
        "context_window_size": 2048,
        "prefill_chunk_size": 2048,
    },
    "codellama_34b": {
        "architectures": ["LlamaForCausalLM"],
        "bos_token_id": 1,
        "eos_token_id": 2,
        "hidden_act": "silu",
        "hidden_size": 8192,
        "initializer_range": 0.02,
        "intermediate_size": 22016,
        "max_position_embeddings": 16384,
        "model_type": "llama",
        "num_attention_heads": 64,
        "num_hidden_layers": 48,
        "num_key_value_heads": 8,
        "pretraining_tp": 1,
        "rms_norm_eps": 1e-05,
        "rope_scaling": None,
        "rope_theta": 1000000,
        "tie_word_embeddings": False,
        "torch_dtype": "bfloat16",
        "transformers_version": "4.32.0.dev0",
        "use_cache": True,
        "vocab_size": 32016,
        "context_window_size": 2048,
        "prefill_chunk_size": 2048,
    },
    "tinyllama_1b_chat_v0.4": {
        "_name_or_path": "/data/tianduo/tinyllama-ft/checkpoint-3890",
        "architectures": ["LlamaForCausalLM"],
        "bos_token_id": 1,
        "eos_token_id": 2,
        "hidden_act": "silu",
        "hidden_size": 2048,
        "initializer_range": 0.02,
        "intermediate_size": 5632,
        "max_position_embeddings": 2048,
        "model_type": "llama",
        "num_attention_heads": 32,
        "num_hidden_layers": 22,
        "num_key_value_heads": 4,
        "pretraining_tp": 1,
        "rms_norm_eps": 1e-05,
        "rope_scaling": None,
        "rope_theta": 10000.0,
        "tie_word_embeddings": False,
        "torch_dtype": "float32",
        "transformers_version": "4.33.1",
        "use_cache": False,
        "vocab_size": 32003,
    },
    "tinyllama_1b_chat_v1.0": {
        "architectures": ["LlamaForCausalLM"],
        "attention_bias": False,
        "bos_token_id": 1,
        "eos_token_id": 2,
        "hidden_act": "silu",
        "hidden_size": 2048,
        "initializer_range": 0.02,
        "intermediate_size": 5632,
        "max_position_embeddings": 2048,
        "model_type": "llama",
        "num_attention_heads": 32,
        "num_hidden_layers": 22,
        "num_key_value_heads": 4,
        "pretraining_tp": 1,
        "rms_norm_eps": 1e-05,
        "rope_scaling": None,
        "rope_theta": 10000.0,
        "tie_word_embeddings": False,
        "torch_dtype": "bfloat16",
        "transformers_version": "4.35.0",
        "use_cache": True,
        "vocab_size": 32000,
    },
    "mistral_7b": {
        "architectures": ["MistralForCausalLM"],
        "bos_token_id": 1,
        "eos_token_id": 2,
        "hidden_act": "silu",
        "hidden_size": 4096,
        "initializer_range": 0.02,
        "intermediate_size": 14336,
        "max_position_embeddings": 32768,
        "model_type": "mistral",
        "num_attention_heads": 32,
        "num_hidden_layers": 32,
        "num_key_value_heads": 8,
        "rms_norm_eps": 1e-05,
        "rope_theta": 10000.0,
        "tie_word_embeddings": False,
        "torch_dtype": "bfloat16",
        "transformers_version": "4.34.0.dev0",
        "use_cache": True,
        "vocab_size": 32000,
        "sliding_window_size": 4096,
        "prefill_chunk_size": 128,
        "attention_sink_size": 4,
    },
    "mistral_7b_v03": {
        "architectures": ["MistralForCausalLM"],
        "attention_dropout": 0.0,
        "bos_token_id": 1,
        "eos_token_id": 2,
        "hidden_act": "silu",
        "hidden_size": 4096,
        "initializer_range": 0.02,
        "intermediate_size": 14336,
        "max_position_embeddings": 32768,
        "model_type": "mistral",
        "num_attention_heads": 32,
        "num_hidden_layers": 32,
        "num_key_value_heads": 8,
        "rms_norm_eps": 1e-05,
        "rope_theta": 1000000.0,
        "sliding_window": None,
        "tie_word_embeddings": False,
        "torch_dtype": "bfloat16",
        "transformers_version": "4.42.0.dev0",
        "use_cache": True,
        "vocab_size": 32768,
    },
    "gpt2": {
        "activation_function": "gelu_new",
        "architectures": ["GPT2LMHeadModel"],
        "attn_pdrop": 0.1,
        "bos_token_id": 50256,
        "embd_pdrop": 0.1,
        "eos_token_id": 50256,
        "initializer_range": 0.02,
        "layer_norm_epsilon": 1e-05,
        "model_type": "gpt2",
        "n_ctx": 1024,
        "n_embd": 768,
        "n_head": 12,
        "n_layer": 12,
        "n_positions": 1024,
        "resid_pdrop": 0.1,
        "summary_activation": None,
        "summary_first_dropout": 0.1,
        "summary_proj_to_labels": True,
        "summary_type": "cls_index",
        "summary_use_proj": True,
        "task_specific_params": {"text-generation": {"do_sample": True, "max_length": 50}},
        "vocab_size": 50257,
    },
    "gpt2_medium": {
        "activation_function": "gelu_new",
        "architectures": ["GPT2LMHeadModel"],
        "attn_pdrop": 0.1,
        "bos_token_id": 50256,
        "embd_pdrop": 0.1,
        "eos_token_id": 50256,
        "initializer_range": 0.02,
        "layer_norm_epsilon": 1e-05,
        "model_type": "gpt2",
        "n_ctx": 1024,
        "n_embd": 1024,
        "n_head": 16,
        "n_layer": 24,
        "n_positions": 1024,
        "n_special": 0,
        "predict_special_tokens": True,
        "resid_pdrop": 0.1,
        "summary_activation": None,
        "summary_first_dropout": 0.1,
        "summary_proj_to_labels": True,
        "summary_type": "cls_index",
        "summary_use_proj": True,
        "task_specific_params": {"text-generation": {"do_sample": True, "max_length": 50}},
        "vocab_size": 50257,
    },
    "gpt_bigcode": {
        "activation_function": "gelu_pytorch_tanh",
        "architectures": ["GPTBigCodeForCausalLM"],
        "attention_softmax_in_fp32": True,
        "multi_query": True,
        "attn_pdrop": 0.1,
        "bos_token_id": 49152,
        "embd_pdrop": 0.1,
        "eos_token_id": 49152,
        "initializer_range": 0.02,
        "layer_norm_epsilon": 1e-05,
        "model_type": "gpt_bigcode",
        "n_embd": 2048,
        "n_head": 16,
        "n_inner": 8192,
        "n_layer": 24,
        "n_positions": 2048,
        "resid_pdrop": 0.1,
        "runner_max_sequence_length": None,
        "scale_attention_softmax_in_fp32": True,
        "scale_attn_weights": True,
        "summary_activation": None,
        "summary_first_dropout": 0.1,
        "summary_proj_to_labels": True,
        "summary_type": "cls_index",
        "summary_use_proj": True,
        "transformers_version": "4.28.0.dev0",
        "use_cache": True,
        "vocab_size": 49280,
    },
    "Mixtral-8x7B-v0.1": {
        "architectures": ["MixtralForCausalLM"],
        "attention_dropout": 0.0,
        "bos_token_id": 1,
        "eos_token_id": 2,
        "hidden_act": "silu",
        "hidden_size": 4096,
        "initializer_range": 0.02,
        "intermediate_size": 14336,
        "max_position_embeddings": 32768,
        "model_type": "mixtral",
        "num_attention_heads": 32,
        "num_experts_per_tok": 2,
        "num_hidden_layers": 32,
        "num_key_value_heads": 8,
        "num_local_experts": 8,
        "output_router_logits": False,
        "rms_norm_eps": 1e-05,
        "rope_theta": 1000000.0,
        "router_aux_loss_coef": 0.02,
        "sliding_window": None,
        "tie_word_embeddings": False,
        "torch_dtype": "bfloat16",
        "transformers_version": "4.36.0.dev0",
        "use_cache": True,
        "vocab_size": 32000,
    },
    "redpajama_3b_v1": {
        "_name_or_path": "/root/fm/models/rp_3b_800b_real_fp16",
        "architectures": ["GPTNeoXForCausalLM"],
        "bos_token_id": 0,
        "eos_token_id": 0,
        "hidden_act": "gelu",
        "hidden_size": 2560,
        "initializer_range": 0.02,
        "intermediate_size": 10240,
        "layer_norm_eps": 1e-05,
        "max_position_embeddings": 2048,
        "model_type": "gpt_neox",
        "num_attention_heads": 32,
        "num_hidden_layers": 32,
        "rotary_emb_base": 10000,
        "rotary_pct": 1.0,
        "tie_word_embeddings": False,
        "torch_dtype": "float16",
        "transformers_version": "4.28.1",
        "use_cache": True,
        "use_parallel_residual": False,
        "vocab_size": 50432,
    },
    "phi-1_5": {
        "_name_or_path": "microsoft/phi-1_5",
        "activation_function": "gelu_new",
        "architectures": ["PhiForCausalLM"],
        "attn_pdrop": 0.0,
        "auto_map": {
            "AutoConfig": "configuration_phi.PhiConfig",
            "AutoModelForCausalLM": "modeling_phi.PhiForCausalLM",
        },
        "embd_pdrop": 0.0,
        "flash_attn": False,
        "flash_rotary": False,
        "fused_dense": False,
        "initializer_range": 0.02,
        "layer_norm_epsilon": 1e-05,
        "model_type": "phi-msft",
        "n_embd": 2048,
        "n_head": 32,
        "n_head_kv": None,
        "n_inner": None,
        "n_layer": 24,
        "n_positions": 2048,
        "resid_pdrop": 0.0,
        "rotary_dim": 32,
        "tie_word_embeddings": False,
        "torch_dtype": "float16",
        "transformers_version": "4.34.1",
        "vocab_size": 51200,
    },
    "phi-2": {
        "_name_or_path": "microsoft/phi-2",
        "activation_function": "gelu_new",
        "architectures": ["PhiForCausalLM"],
        "attn_pdrop": 0.0,
        "auto_map": {
            "AutoConfig": "configuration_phi.PhiConfig",
            "AutoModelForCausalLM": "modeling_phi.PhiForCausalLM",
        },
        "embd_pdrop": 0.0,
        "flash_attn": False,
        "flash_rotary": False,
        "fused_dense": False,
        "img_processor": None,
        "initializer_range": 0.02,
        "layer_norm_epsilon": 1e-05,
        "model_type": "phi-msft",
        "n_embd": 2560,
        "n_head": 32,
        "n_head_kv": None,
        "n_inner": None,
        "n_layer": 32,
        "n_positions": 2048,
        "resid_pdrop": 0.1,
        "rotary_dim": 32,
        "tie_word_embeddings": False,
        "torch_dtype": "float16",
        "transformers_version": "4.35.2",
        "vocab_size": 51200,
    },
    "phi-3": {
        "_name_or_path": "Phi-3-mini-4k-instruct",
        "architectures": ["Phi3ForCausalLM"],
        "attention_dropout": 0.0,
        "auto_map": {
            "AutoConfig": "configuration_phi3.Phi3Config",
            "AutoModelForCausalLM": "modeling_phi3.Phi3ForCausalLM",
        },
        "bos_token_id": 1,
        "embd_pdrop": 0.0,
        "eos_token_id": 32000,
        "hidden_act": "silu",
        "hidden_size": 3072,
        "initializer_range": 0.02,
        "intermediate_size": 8192,
        "max_position_embeddings": 4096,
        "model_type": "phi3",
        "num_attention_heads": 32,
        "num_hidden_layers": 32,
        "num_key_value_heads": 32,
        "original_max_position_embeddings": 4096,
        "pad_token_id": 32000,
        "resid_pdrop": 0.0,
        "rms_norm_eps": 1e-05,
        "rope_scaling": None,
        "rope_theta": 10000.0,
        "sliding_window": 2047,
        "tie_word_embeddings": False,
        "torch_dtype": "bfloat16",
        "transformers_version": "4.39.3",
        "use_cache": True,
        "vocab_size": 32064,
    },
    "qwen": {
        "architectures": ["QWenLMHeadModel"],
        "auto_map": {
            "AutoConfig": "configuration_qwen.QWenConfig",
            "AutoModelForCausalLM": "modeling_qwen.QWenLMHeadModel",
        },
        "attn_dropout_prob": 0.0,
        "bf16": False,
        "emb_dropout_prob": 0.0,
        "hidden_size": 2048,
        "intermediate_size": 11008,
        "initializer_range": 0.02,
        "kv_channels": 128,
        "layer_norm_epsilon": 1e-06,
        "max_position_embeddings": 8192,
        "model_type": "qwen",
        "no_bias": True,
        "num_attention_heads": 16,
        "num_hidden_layers": 24,
        "rotary_emb_base": 10000,
        "rotary_pct": 1.0,
        "scale_attn_weights": True,
        "seq_length": 8192,
        "tie_word_embeddings": False,
        "tokenizer_class": "QWenTokenizer",
        "transformers_version": "4.32.0",
        "use_cache": True,
        "use_dynamic_ntk": True,
        "use_flash_attn": "auto",
        "use_logn_attn": True,
        "vocab_size": 151936,
    },
    "qwen2": {
        "_name_or_path": "Qwen/Qwen1.5-1.8B-Chat",
        "architectures": ["Qwen2ForCausalLM"],
        "attention_dropout": 0.0,
        "bos_token_id": 151643,
        "eos_token_id": 151645,
        "hidden_act": "silu",
        "hidden_size": 2048,
        "initializer_range": 0.02,
        "intermediate_size": 5504,
        "max_position_embeddings": 4096,
        "max_window_layers": 21,
        "model_type": "qwen2",
        "num_attention_heads": 16,
        "num_hidden_layers": 24,
        "num_key_value_heads": 16,
        "rms_norm_eps": 1e-06,
        "rope_theta": 1000000.0,
        "sliding_window": 32768,
        "tie_word_embeddings": True,
        "torch_dtype": "bfloat16",
        "transformers_version": "4.37.2",
        "use_cache": True,
        "use_sliding_window": False,
        "vocab_size": 151936,
    },
    "qwen2moe": {
        "architectures": ["Qwen2MoeForCausalLM"],
        "attention_dropout": 0.0,
        "bos_token_id": 151643,
        "eos_token_id": 151645,
        "hidden_act": "silu",
        "hidden_size": 2048,
        "initializer_range": 0.02,
        "intermediate_size": 5632,
        "max_position_embeddings": 32768,
        "max_window_layers": 21,
        "model_type": "qwen2_moe",
        "num_attention_heads": 16,
        "num_hidden_layers": 24,
        "num_key_value_heads": 16,
        "rms_norm_eps": 1e-06,
        "rope_theta": 1000000.0,
        "sliding_window": 32768,
        "tie_word_embeddings": False,
        "torch_dtype": "bfloat16",
        "transformers_version": "4.39.0.dev0",
        "use_cache": True,
        "use_sliding_window": False,
        "vocab_size": 151936,
        "decoder_sparse_step": 1,
        "moe_intermediate_size": 1408,
        "shared_expert_intermediate_size": 5632,
        "num_experts_per_tok": 4,
        "num_experts": 60,
        "norm_topk_prob": False,
        "output_router_logits": False,
        "router_aux_loss_coef": 0.001,
    },
    "stablelm": {
        "architectures": ["StableLmForCausalLM"],
        "bos_token_id": 0,
        "eos_token_id": 0,
        "hidden_act": "silu",
        "hidden_size": 2560,
        "initializer_range": 0.02,
        "intermediate_size": 6912,
        "max_position_embeddings": 4096,
        "model_type": "stablelm",
        "layer_norm_eps": 1e-05,
        "num_attention_heads": 32,
        "num_hidden_layers": 32,
        "num_key_value_heads": 32,
        "partial_rotary_factor": 0.25,
        "rope_theta": 10000,
        "tie_word_embeddings": False,
        "torch_dtype": "bfloat16",
        "transformers_version": "4.38.0",
        "use_cache": True,
        "use_qkv_bias": False,
        "vocab_size": 50304,
    },
    "baichuan": {
        "architectures": ["BaichuanForCausalLM"],
        "auto_map": {
            "AutoConfig": "configuration_baichuan.BaichuanConfig",
            "AutoModelForCausalLM": "modeling_baichuan.BaichuanForCausalLM",
        },
        "tokenizer_class": "BaichuanTokenizer",
        "bos_token_id": 1,
        "eos_token_id": 2,
        "hidden_size": 4096,
        "initializer_range": 0.02,
        "intermediate_size": 11008,
        "max_position_embeddings": 4096,
        "model_max_length": 4096,
        "model_type": "baichuan",
        "num_attention_heads": 32,
        "num_hidden_layers": 32,
        "pad_token_id": 0,
        "rms_norm_eps": 1e-06,
        "_from_model_config": True,
        "tie_word_embeddings": False,
        "torch_dtype": "bfloat16",
        "transformers_version": "4.29.2",
        "use_cache": True,
        "vocab_size": 125696,
    },
    "internlm": {
        "architectures": ["InternLMForCausalLM"],
        "auto_map": {
            "AutoConfig": "configuration_internlm.InternLMConfig",
            "AutoModel": "modeling_internlm.InternLMForCausalLM",
            "AutoModelForCausalLM": "modeling_internlm.InternLMForCausalLM",
        },
        "bias": True,
        "bos_token_id": 1,
        "eos_token_id": 2,
        "hidden_act": "silu",
        "hidden_size": 4096,
        "initializer_range": 0.02,
        "intermediate_size": 11008,
        "max_position_embeddings": 2048,
        "model_type": "internlm",
        "num_attention_heads": 32,
        "num_hidden_layers": 32,
        "pad_token_id": 2,
        "rms_norm_eps": 1e-06,
        "tie_word_embeddings": False,
        "torch_dtype": "float16",
        "transformers_version": "4.33.2",
        "use_cache": True,
        "vocab_size": 103168,
    },
    # TODO(mlc-team): enable the model presets when stabilized.
    # "gemma_2b": {
    #     "architectures": ["GemmaForCausalLM"],
    #     "attention_bias": False,
    #     "bos_token_id": 2,
    #     "eos_token_id": 1,
    #     "head_dim": 256,
    #     "hidden_act": "gelu",
    #     "hidden_size": 2048,
    #     "initializer_range": 0.02,
    #     "intermediate_size": 16384,
    #     "max_position_embeddings": 8192,
    #     "model_type": "gemma",
    #     "num_attention_heads": 8,
    #     "num_hidden_layers": 18,
    #     "num_key_value_heads": 1,
    #     "pad_token_id": 0,
    #     "rms_norm_eps": 1e-06,
    #     "rope_theta": 10000.0,
    #     "torch_dtype": "bfloat16",
    #     "transformers_version": "4.38.0.dev0",
    #     "vocab_size": 256000,
    # },
    # "gemma_7b": {
    #     "architectures": ["GemmaForCausalLM"],
    #     "attention_bias": False,
    #     "bos_token_id": 2,
    #     "eos_token_id": 1,
    #     "head_dim": 256,
    #     "hidden_act": "gelu",
    #     "hidden_size": 3072,
    #     "initializer_range": 0.02,
    #     "intermediate_size": 24576,
    #     "max_position_embeddings": 8192,
    #     "model_type": "gemma",
    #     "num_attention_heads": 16,
    #     "num_hidden_layers": 28,
    #     "num_key_value_heads": 16,
    #     "pad_token_id": 0,
    #     "rms_norm_eps": 1e-06,
    #     "rope_theta": 10000.0,
    #     "torch_dtype": "bfloat16",
    #     "transformers_version": "4.38.0.dev0",
    #     "vocab_size": 256000,
    # },
    "rwkv5_3b": {
        "architectures": ["RwkvForCausalLM"],
        "auto_map": {
            "AutoConfig": "configuration_rwkv5.Rwkv5Config",
            "AutoModelForCausalLM": "modeling_rwkv5.RwkvForCausalLM",
        },
        "attention_hidden_size": 2560,
        "bos_token_id": 0,
        "context_length": 4096,
        "eos_token_id": 0,
        "head_size": 64,
        "hidden_size": 2560,
        "intermediate_size": None,
        "layer_norm_epsilon": 1e-05,
        "model_type": "rwkv5",
        "model_version": "5_2",
        "num_hidden_layers": 32,
        "rescale_every": 6,
        "tie_word_embeddings": True,
        "transformers_version": "4.34.0",
        "use_cache": True,
        "vocab_size": 65536,
    },
    "orion": {
        "architectures": ["OrionForCausalLM"],
        "auto_map": {
            "AutoConfig": "configuration_orion.OrionConfig",
            "AutoModelForCausalLM": "modeling_orion.OrionForCausalLM",
        },
        "tokenizer_class": "OrionTokenizer",
        "bos_token_id": 1,
        "eos_token_id": 2,
        "hidden_act": "silu",
        "hidden_size": 5120,
        "model_type": "orion",
        "initializer_range": 0.02,
        "intermediate_size": 15360,
        "max_position_embeddings": 4096,
        "max_sequence_length": 4096,
        "num_attention_heads": 40,
        "num_hidden_layers": 40,
        "num_key_value_heads": 40,
        "pad_token_id": 0,
        "pretraining_tp": 1,
        "rms_norm_eps": 1e-05,
        "rope_scaling": None,
        "rope_theta": 10000.0,
        "tie_word_embeddings": False,
        "torch_dtype": "bfloat16",
        "transformers_version": "4.34.0",
        "use_cache": True,
        "vocab_size": 84608,
    },
    "llava": {
        "architectures": ["LlavaForConditionalGeneration"],
        "ignore_index": -100,
        "image_token_index": 32000,
        "model_type": "llava",
        "pad_token_id": 32001,
        "projector_hidden_act": "gelu",
        "text_config": {
            "_name_or_path": "meta-llama/Llama-2-7b-hf",
            "architectures": ["LlamaForCausalLM"],
            "max_position_embeddings": 4096,
            "model_type": "llama",
            "rms_norm_eps": 1e-05,
            "torch_dtype": "float16",
            "vocab_size": 32064,
        },
        "tie_word_embeddings": False,
        "torch_dtype": "float16",
        "transformers_version": "4.36.0.dev0",
        "vision_config": {
            "hidden_size": 1024,
            "image_size": 336,
            "intermediate_size": 4096,
            "model_type": "clip_vision_model",
            "num_attention_heads": 16,
            "num_hidden_layers": 24,
            "patch_size": 14,
            "projection_dim": 768,
            "vocab_size": 32000,
        },
        "vision_feature_layer": -2,
        "vision_feature_select_strategy": "default",
        "vocab_size": 32064,
    },
    "chatglm": {
        "architectures": ["ChatGLMModel"],
        "model_type": "chatglm",
        "auto_map": {
            "AutoConfig": "configuration_chatglm.ChatGLMConfig",
            "AutoModel": "modeling_chatglm.ChatGLMForConditionalGeneration",
            "AutoModelForCausalLM": "modeling_chatglm.ChatGLMForConditionalGeneration",
        },
        "add_bias_linear": False,
        "add_qkv_bias": True,
        "apply_query_key_layer_scaling": True,
        "apply_residual_connection_post_layernorm": False,
        "attention_dropout": 0.0,
        "attention_softmax_in_fp32": True,
        "bias_dropout_fusion": True,
        "ffn_hidden_size": 13696,
        "fp32_residual_connection": False,
        "hidden_dropout": 0.0,
        "hidden_size": 4096,
        "kv_channels": 128,
        "layernorm_epsilon": 1e-05,
        "multi_query_attention": True,
        "multi_query_group_num": 2,
        "num_attention_heads": 32,
        "num_layers": 28,
        "original_rope": True,
        "padded_vocab_size": 65024,
        "post_layer_norm": True,
        "rmsnorm": True,
        "seq_length": 8192,
        "use_cache": True,
        "torch_dtype": "float16",
        "transformers_version": "4.30.2",
        "tie_word_embeddings": False,
        "eos_token_id": 2,
        "pad_token_id": 0,
    },
    "llama3_8b": {
        "architectures": ["LlamaForCausalLM"],
        "attention_bias": False,
        "attention_dropout": 0.0,
        "bos_token_id": 128000,
        "eos_token_id": 128001,
        "hidden_act": "silu",
        "hidden_size": 4096,
        "initializer_range": 0.02,
        "intermediate_size": 14336,
        "max_position_embeddings": 8192,
        "model_type": "llama",
        "num_attention_heads": 32,
        "num_hidden_layers": 32,
        "num_key_value_heads": 8,
        "pretraining_tp": 1,
        "rms_norm_eps": 1e-05,
        "rope_scaling": None,
        "rope_theta": 500000.0,
        "tie_word_embeddings": False,
        "torch_dtype": "bfloat16",
        "transformers_version": "4.40.0.dev0",
        "use_cache": True,
        "vocab_size": 128256,
    },
    "llama3_70b": {
        "architectures": ["LlamaForCausalLM"],
        "attention_bias": False,
        "attention_dropout": 0.0,
        "bos_token_id": 128000,
        "eos_token_id": 128001,
        "hidden_act": "silu",
        "hidden_size": 8192,
        "initializer_range": 0.02,
        "intermediate_size": 28672,
        "max_position_embeddings": 8192,
        "model_type": "llama",
        "num_attention_heads": 64,
        "num_hidden_layers": 80,
        "num_key_value_heads": 8,
        "pretraining_tp": 1,
        "rms_norm_eps": 1e-05,
        "rope_scaling": None,
        "rope_theta": 500000.0,
        "tie_word_embeddings": False,
        "torch_dtype": "bfloat16",
        "transformers_version": "4.40.0.dev0",
        "use_cache": True,
        "vocab_size": 128256,
    },
    "bert": {
        "architectures": ["BertModel"],
        "attention_probs_dropout_prob": 0.1,
        "gradient_checkpointing": False,
        "hidden_act": "gelu",
        "hidden_dropout_prob": 0.1,
        "hidden_size": 768,
        "initializer_range": 0.02,
        "intermediate_size": 3072,
        "layer_norm_eps": 1e-12,
        "max_position_embeddings": 512,
        "model_type": "bert",
        "num_attention_heads": 12,
        "num_hidden_layers": 12,
        "pad_token_id": 0,
        "position_embedding_type": "absolute",
        "transformers_version": "4.6.0.dev0",
        "type_vocab_size": 2,
        "vocab_size": 30522,
    },
    "stablelm-2-zephyr-1_6b": {
        "architectures": ["StableLmForCausalLM"],
        "bos_token_id": 100257,
        "eos_token_id": 100257,
        "hidden_act": "silu",
        "hidden_size": 2048,
        "initializer_range": 0.02,
        "intermediate_size": 5632,
        "max_position_embeddings": 4096,
        "model_type": "stablelm",
        "layer_norm_eps": 1e-05,
        "num_attention_heads": 32,
        "num_hidden_layers": 24,
        "num_key_value_heads": 32,
        "partial_rotary_factor": 0.25,
        "rope_theta": 10000,
        "tie_word_embeddings": False,
        "torch_dtype": "float16",
        "transformers_version": "4.38.0",
        "use_cache": True,
        "use_qkv_bias": True,
        "vocab_size": 100352,
    },
    "qwen2_0_5b": {
        "architectures": ["Qwen2ForCausalLM"],
        "attention_dropout": 0.0,
        "bos_token_id": 151643,
        "eos_token_id": 151645,
        "hidden_act": "silu",
        "hidden_size": 896,
        "initializer_range": 0.02,
        "intermediate_size": 4864,
        "max_position_embeddings": 32768,
        "max_window_layers": 24,
        "model_type": "qwen2",
        "num_attention_heads": 14,
        "num_hidden_layers": 24,
        "num_key_value_heads": 2,
        "rms_norm_eps": 1e-06,
        "rope_theta": 1000000.0,
        "sliding_window": 32768,
        "tie_word_embeddings": True,
        "torch_dtype": "bfloat16",
        "transformers_version": "4.40.1",
        "use_cache": True,
        "use_sliding_window": False,
        "vocab_size": 151936,
    },
    "qwen2_1_5b": {
        "architectures": ["Qwen2ForCausalLM"],
        "attention_dropout": 0.0,
        "bos_token_id": 151643,
        "eos_token_id": 151645,
        "hidden_act": "silu",
        "hidden_size": 1536,
        "initializer_range": 0.02,
        "intermediate_size": 8960,
        "max_position_embeddings": 32768,
        "max_window_layers": 28,
        "model_type": "qwen2",
        "num_attention_heads": 12,
        "num_hidden_layers": 28,
        "num_key_value_heads": 2,
        "rms_norm_eps": 1e-06,
        "rope_theta": 1000000.0,
        "sliding_window": 32768,
        "tie_word_embeddings": True,
        "torch_dtype": "bfloat16",
        "transformers_version": "4.40.1",
        "use_cache": True,
        "use_sliding_window": False,
        "vocab_size": 151936,
    },
    "qwen2_7b": {
        "architectures": ["Qwen2ForCausalLM"],
        "attention_dropout": 0.0,
        "bos_token_id": 151643,
        "eos_token_id": 151645,
        "hidden_act": "silu",
        "hidden_size": 3584,
        "initializer_range": 0.02,
        "intermediate_size": 18944,
        "max_position_embeddings": 32768,
        "max_window_layers": 28,
        "model_type": "qwen2",
        "num_attention_heads": 28,
        "num_hidden_layers": 28,
        "num_key_value_heads": 4,
        "rms_norm_eps": 1e-06,
        "rope_theta": 1000000.0,
        "sliding_window": 131072,
        "tie_word_embeddings": False,
        "torch_dtype": "bfloat16",
        "transformers_version": "4.41.2",
        "use_cache": True,
        "use_sliding_window": False,
        "vocab_size": 152064,
    },
    "internlm2": {
        "architectures": ["InternLM2ForCausalLM"],
        "attn_implementation": "eager",
        "auto_map": {
            "AutoConfig": "configuration_internlm2.InternLM2Config",
            "AutoModelForCausalLM": "modeling_internlm2.InternLM2ForCausalLM",
            "AutoModel": "modeling_internlm2.InternLM2ForCausalLM",
        },
        "bias": False,
        "bos_token_id": 1,
        "eos_token_id": 2,
        "hidden_act": "silu",
        "hidden_size": 4096,
        "initializer_range": 0.02,
        "intermediate_size": 14336,
        "max_position_embeddings": 32768,
        "model_type": "internlm2",
        "num_attention_heads": 32,
        "num_hidden_layers": 32,
        "num_key_value_heads": 8,
        "pad_token_id": 2,
        "rms_norm_eps": 1e-05,
        "rope_scaling": None,
        "rope_theta": 1000000,
        "tie_word_embeddings": False,
        "torch_dtype": "bfloat16",
        "transformers_version": "4.37.1",
        "use_cache": True,
        "vocab_size": 92544,
    },
    "internlm2_5_7b": {
        "architectures": ["InternLM2ForCausalLM"],
        "attn_implementation": "eager",
        "auto_map": {
            "AutoConfig": "configuration_internlm2.InternLM2Config",
            "AutoModelForCausalLM": "modeling_internlm2.InternLM2ForCausalLM",
            "AutoModel": "modeling_internlm2.InternLM2ForCausalLM"
        },
        "bias": False,
        "bos_token_id": 1,
        "eos_token_id": 2,
        "hidden_act": "silu",
        "hidden_size": 4096,
        "initializer_range": 0.02,
        "intermediate_size": 14336,
        "max_position_embeddings": 32768,
        "model_type": "internlm2",
        "num_attention_heads": 32,
        "num_hidden_layers": 32,
        "num_key_value_heads": 8,
        "pad_token_id": 2,
        "rms_norm_eps": 1e-05,
        "rope_scaling": {"type": "dynamic","factor": 2.0},
        "rope_theta": 1000000,
        "tie_word_embeddings": False,
        "torch_dtype": "bfloat16",
        "transformers_version": "4.41.0",
        "use_cache": True,
        "vocab_size": 92544,
        "pretraining_tp": 1,
    },
}
