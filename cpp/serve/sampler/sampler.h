/*!
 *  Copyright (c) 2023 by Contributors
 * \file serve/sampler/sampler.h
 * \brief The header for runtime module of sampler functions.
 */

#ifndef MLC_LLM_SERVE_SAMPLER_SAMPLER_H_
#define MLC_LLM_SERVE_SAMPLER_SAMPLER_H_

#include <tvm/runtime/container/string.h>
#include <tvm/runtime/module.h>

#include "../../base.h"
#include "../../random.h"
#include "../data.h"
#include "../event_trace_recorder.h"
#include "../model.h"
#include "../request_state.h"

namespace mlc {
namespace llm {
namespace serve {

using tvm::Device;
using namespace tvm::runtime;

/*!
 * \brief The base class of runtime sampler.
 * Its main function is `BatchSampleTokens`, which takes a batch of
 * logits and corresponding configuration, and sample one token
 * for each instance of the batch.
 */
class SamplerObj : public Object {
 public:
  /*!
   * \brief Sample tokens from the input batch of prob distribution on device.
   * \param probs_on_device The prob distributions on GPU to sample tokens from.
   * \param sample_indices Specifying which request we should sample for
   * in i-th output. The output result is sample as follow:
   *   result[i] = sample_from(prob_on_device[sample_indices[i],:], generation_config[i]));
   * \param request_ids The id of each request.
   * \param generation_cfg The generation config of each request
   * in the input batch.
   * \param rngs The random number generator of each sequence.
   * \param output_prob_dist The output probability distribution
   * \return The batch of sampling results, which contain the sampled token id
   * and other probability info.
   */
  virtual std::vector<SampleResult> BatchSampleTokens(
      NDArray probs_on_device,                        //
      const std::vector<int>& sample_indices,         //
      const Array<String>& request_ids,               //
      const Array<GenerationConfig>& generation_cfg,  //
      const std::vector<RandomGenerator*>& rngs,      //
      std::vector<NDArray>* output_prob_dist = nullptr) = 0;

  /*!
   * \brief Verify draft tokens generated by small models in the large model
   * in speculative decoding. The input corresponds to a batch of sequences.
   * \param probs_on_device The prob distributions on GPU to sample tokens from.
   * \param request_ids The id of each request.
   * \param cum_verify_lengths The cumulative draft lengths to verify of all sequences.
   * \param generation_cfg The generation config of each request
   * in the input batch.
   * \param rngs The random number generator of each sequence.
   * \param draft_output_tokens The draft tokens generated by the small model for
   * each sequence.
   * \param draft_output_prob_dist The probability distribution computed from the
   * small model for each sequence.
   * \return The list of accepted tokens for each request.
   */
  virtual std::vector<std::vector<SampleResult>> BatchVerifyDraftTokens(
      NDArray probs_on_device, const Array<String>& request_ids,
      const std::vector<int>& cum_verify_lengths, const Array<GenerationConfig>& generation_cfg,
      const std::vector<RandomGenerator*>& rngs,
      const std::vector<std::vector<SampleResult>>& draft_output_tokens,
      const std::vector<std::vector<NDArray>>& draft_output_prob_dist) = 0;

  static constexpr const char* _type_key = "mlc.serve.Sampler";
  static constexpr const bool _type_has_method_sequal_reduce = false;
  static constexpr const bool _type_has_method_shash_reduce = false;
  TVM_DECLARE_BASE_OBJECT_INFO(SamplerObj, Object);
};

class Sampler : public ObjectRef {
 public:
  /*! * \brief Create a CPU sampler. */
  TVM_DLL static Sampler CreateCPUSampler(Optional<EventTraceRecorder> trace_recorder);
  /*!
   * \brief Create a GPU sampler.
   * \param max_num_sample The max number of samples to sample at a time.
   * \param vocab_size The model's vocabulary size.
   * \param ft The packed function table.
   * \param device The device that the model runs on.
   * \param trace_recorder The event trace recorder.
   */
  TVM_DLL static Sampler CreateGPUSampler(int max_num_sample, int vocab_size, FunctionTable* ft,
                                          DLDevice device,
                                          Optional<EventTraceRecorder> trace_recorder);

  /*! \brief Check if the given device supports GPU sampling. */
  static bool SupportGPUSampler(Device device) {
    return device.device_type == DLDeviceType::kDLCUDA;
  }

  TVM_DEFINE_MUTABLE_OBJECT_REF_METHODS(Sampler, ObjectRef, SamplerObj);
};

}  // namespace serve
}  // namespace llm
}  // namespace mlc

#endif  // MLC_LLM_SERVE_SAMPLER_SAMPLER_H_
