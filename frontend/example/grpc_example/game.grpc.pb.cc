// Generated by the gRPC C++ plugin.
// If you make any local change, they will be lost.
// source: game.proto

#include "game.pb.h"
#include "game.grpc.pb.h"

#include <functional>
#include <grpcpp/support/async_stream.h>
#include <grpcpp/support/async_unary_call.h>
#include <grpcpp/impl/channel_interface.h>
#include <grpcpp/impl/client_unary_call.h>
#include <grpcpp/support/client_callback.h>
#include <grpcpp/support/message_allocator.h>
#include <grpcpp/support/method_handler.h>
#include <grpcpp/impl/rpc_service_method.h>
#include <grpcpp/support/server_callback.h>
#include <grpcpp/impl/server_callback_handlers.h>
#include <grpcpp/server_context.h>
#include <grpcpp/impl/service_type.h>
#include <grpcpp/support/sync_stream.h>

static const char* Game_method_names[] = {
  "/Game/GetGameMeta",
  "/Game/SetGameMeta",
  "/Game/Reset",
  "/Game/SuggestNextMove",
  "/Game/GetLastGameState",
};

std::unique_ptr< Game::Stub> Game::NewStub(const std::shared_ptr< ::grpc::ChannelInterface>& channel, const ::grpc::StubOptions& options) {
  (void)options;
  std::unique_ptr< Game::Stub> stub(new Game::Stub(channel, options));
  return stub;
}

Game::Stub::Stub(const std::shared_ptr< ::grpc::ChannelInterface>& channel, const ::grpc::StubOptions& options)
  : channel_(channel), rpcmethod_GetGameMeta_(Game_method_names[0], options.suffix_for_stats(),::grpc::internal::RpcMethod::NORMAL_RPC, channel)
  , rpcmethod_SetGameMeta_(Game_method_names[1], options.suffix_for_stats(),::grpc::internal::RpcMethod::NORMAL_RPC, channel)
  , rpcmethod_Reset_(Game_method_names[2], options.suffix_for_stats(),::grpc::internal::RpcMethod::NORMAL_RPC, channel)
  , rpcmethod_SuggestNextMove_(Game_method_names[3], options.suffix_for_stats(),::grpc::internal::RpcMethod::NORMAL_RPC, channel)
  , rpcmethod_GetLastGameState_(Game_method_names[4], options.suffix_for_stats(),::grpc::internal::RpcMethod::NORMAL_RPC, channel)
  {}

::grpc::Status Game::Stub::GetGameMeta(::grpc::ClientContext* context, const ::Empty& request, ::GameMeta* response) {
  return ::grpc::internal::BlockingUnaryCall< ::Empty, ::GameMeta, ::grpc::protobuf::MessageLite, ::grpc::protobuf::MessageLite>(channel_.get(), rpcmethod_GetGameMeta_, context, request, response);
}

void Game::Stub::async::GetGameMeta(::grpc::ClientContext* context, const ::Empty* request, ::GameMeta* response, std::function<void(::grpc::Status)> f) {
  ::grpc::internal::CallbackUnaryCall< ::Empty, ::GameMeta, ::grpc::protobuf::MessageLite, ::grpc::protobuf::MessageLite>(stub_->channel_.get(), stub_->rpcmethod_GetGameMeta_, context, request, response, std::move(f));
}

void Game::Stub::async::GetGameMeta(::grpc::ClientContext* context, const ::Empty* request, ::GameMeta* response, ::grpc::ClientUnaryReactor* reactor) {
  ::grpc::internal::ClientCallbackUnaryFactory::Create< ::grpc::protobuf::MessageLite, ::grpc::protobuf::MessageLite>(stub_->channel_.get(), stub_->rpcmethod_GetGameMeta_, context, request, response, reactor);
}

::grpc::ClientAsyncResponseReader< ::GameMeta>* Game::Stub::PrepareAsyncGetGameMetaRaw(::grpc::ClientContext* context, const ::Empty& request, ::grpc::CompletionQueue* cq) {
  return ::grpc::internal::ClientAsyncResponseReaderHelper::Create< ::GameMeta, ::Empty, ::grpc::protobuf::MessageLite, ::grpc::protobuf::MessageLite>(channel_.get(), cq, rpcmethod_GetGameMeta_, context, request);
}

::grpc::ClientAsyncResponseReader< ::GameMeta>* Game::Stub::AsyncGetGameMetaRaw(::grpc::ClientContext* context, const ::Empty& request, ::grpc::CompletionQueue* cq) {
  auto* result =
    this->PrepareAsyncGetGameMetaRaw(context, request, cq);
  result->StartCall();
  return result;
}

::grpc::Status Game::Stub::SetGameMeta(::grpc::ClientContext* context, const ::GameMeta& request, ::Empty* response) {
  return ::grpc::internal::BlockingUnaryCall< ::GameMeta, ::Empty, ::grpc::protobuf::MessageLite, ::grpc::protobuf::MessageLite>(channel_.get(), rpcmethod_SetGameMeta_, context, request, response);
}

void Game::Stub::async::SetGameMeta(::grpc::ClientContext* context, const ::GameMeta* request, ::Empty* response, std::function<void(::grpc::Status)> f) {
  ::grpc::internal::CallbackUnaryCall< ::GameMeta, ::Empty, ::grpc::protobuf::MessageLite, ::grpc::protobuf::MessageLite>(stub_->channel_.get(), stub_->rpcmethod_SetGameMeta_, context, request, response, std::move(f));
}

void Game::Stub::async::SetGameMeta(::grpc::ClientContext* context, const ::GameMeta* request, ::Empty* response, ::grpc::ClientUnaryReactor* reactor) {
  ::grpc::internal::ClientCallbackUnaryFactory::Create< ::grpc::protobuf::MessageLite, ::grpc::protobuf::MessageLite>(stub_->channel_.get(), stub_->rpcmethod_SetGameMeta_, context, request, response, reactor);
}

::grpc::ClientAsyncResponseReader< ::Empty>* Game::Stub::PrepareAsyncSetGameMetaRaw(::grpc::ClientContext* context, const ::GameMeta& request, ::grpc::CompletionQueue* cq) {
  return ::grpc::internal::ClientAsyncResponseReaderHelper::Create< ::Empty, ::GameMeta, ::grpc::protobuf::MessageLite, ::grpc::protobuf::MessageLite>(channel_.get(), cq, rpcmethod_SetGameMeta_, context, request);
}

::grpc::ClientAsyncResponseReader< ::Empty>* Game::Stub::AsyncSetGameMetaRaw(::grpc::ClientContext* context, const ::GameMeta& request, ::grpc::CompletionQueue* cq) {
  auto* result =
    this->PrepareAsyncSetGameMetaRaw(context, request, cq);
  result->StartCall();
  return result;
}

::grpc::Status Game::Stub::Reset(::grpc::ClientContext* context, const ::Empty& request, ::Empty* response) {
  return ::grpc::internal::BlockingUnaryCall< ::Empty, ::Empty, ::grpc::protobuf::MessageLite, ::grpc::protobuf::MessageLite>(channel_.get(), rpcmethod_Reset_, context, request, response);
}

void Game::Stub::async::Reset(::grpc::ClientContext* context, const ::Empty* request, ::Empty* response, std::function<void(::grpc::Status)> f) {
  ::grpc::internal::CallbackUnaryCall< ::Empty, ::Empty, ::grpc::protobuf::MessageLite, ::grpc::protobuf::MessageLite>(stub_->channel_.get(), stub_->rpcmethod_Reset_, context, request, response, std::move(f));
}

void Game::Stub::async::Reset(::grpc::ClientContext* context, const ::Empty* request, ::Empty* response, ::grpc::ClientUnaryReactor* reactor) {
  ::grpc::internal::ClientCallbackUnaryFactory::Create< ::grpc::protobuf::MessageLite, ::grpc::protobuf::MessageLite>(stub_->channel_.get(), stub_->rpcmethod_Reset_, context, request, response, reactor);
}

::grpc::ClientAsyncResponseReader< ::Empty>* Game::Stub::PrepareAsyncResetRaw(::grpc::ClientContext* context, const ::Empty& request, ::grpc::CompletionQueue* cq) {
  return ::grpc::internal::ClientAsyncResponseReaderHelper::Create< ::Empty, ::Empty, ::grpc::protobuf::MessageLite, ::grpc::protobuf::MessageLite>(channel_.get(), cq, rpcmethod_Reset_, context, request);
}

::grpc::ClientAsyncResponseReader< ::Empty>* Game::Stub::AsyncResetRaw(::grpc::ClientContext* context, const ::Empty& request, ::grpc::CompletionQueue* cq) {
  auto* result =
    this->PrepareAsyncResetRaw(context, request, cq);
  result->StartCall();
  return result;
}

::grpc::Status Game::Stub::SuggestNextMove(::grpc::ClientContext* context, const ::GameState& request, ::GameState* response) {
  return ::grpc::internal::BlockingUnaryCall< ::GameState, ::GameState, ::grpc::protobuf::MessageLite, ::grpc::protobuf::MessageLite>(channel_.get(), rpcmethod_SuggestNextMove_, context, request, response);
}

void Game::Stub::async::SuggestNextMove(::grpc::ClientContext* context, const ::GameState* request, ::GameState* response, std::function<void(::grpc::Status)> f) {
  ::grpc::internal::CallbackUnaryCall< ::GameState, ::GameState, ::grpc::protobuf::MessageLite, ::grpc::protobuf::MessageLite>(stub_->channel_.get(), stub_->rpcmethod_SuggestNextMove_, context, request, response, std::move(f));
}

void Game::Stub::async::SuggestNextMove(::grpc::ClientContext* context, const ::GameState* request, ::GameState* response, ::grpc::ClientUnaryReactor* reactor) {
  ::grpc::internal::ClientCallbackUnaryFactory::Create< ::grpc::protobuf::MessageLite, ::grpc::protobuf::MessageLite>(stub_->channel_.get(), stub_->rpcmethod_SuggestNextMove_, context, request, response, reactor);
}

::grpc::ClientAsyncResponseReader< ::GameState>* Game::Stub::PrepareAsyncSuggestNextMoveRaw(::grpc::ClientContext* context, const ::GameState& request, ::grpc::CompletionQueue* cq) {
  return ::grpc::internal::ClientAsyncResponseReaderHelper::Create< ::GameState, ::GameState, ::grpc::protobuf::MessageLite, ::grpc::protobuf::MessageLite>(channel_.get(), cq, rpcmethod_SuggestNextMove_, context, request);
}

::grpc::ClientAsyncResponseReader< ::GameState>* Game::Stub::AsyncSuggestNextMoveRaw(::grpc::ClientContext* context, const ::GameState& request, ::grpc::CompletionQueue* cq) {
  auto* result =
    this->PrepareAsyncSuggestNextMoveRaw(context, request, cq);
  result->StartCall();
  return result;
}

::grpc::Status Game::Stub::GetLastGameState(::grpc::ClientContext* context, const ::Empty& request, ::GameState* response) {
  return ::grpc::internal::BlockingUnaryCall< ::Empty, ::GameState, ::grpc::protobuf::MessageLite, ::grpc::protobuf::MessageLite>(channel_.get(), rpcmethod_GetLastGameState_, context, request, response);
}

void Game::Stub::async::GetLastGameState(::grpc::ClientContext* context, const ::Empty* request, ::GameState* response, std::function<void(::grpc::Status)> f) {
  ::grpc::internal::CallbackUnaryCall< ::Empty, ::GameState, ::grpc::protobuf::MessageLite, ::grpc::protobuf::MessageLite>(stub_->channel_.get(), stub_->rpcmethod_GetLastGameState_, context, request, response, std::move(f));
}

void Game::Stub::async::GetLastGameState(::grpc::ClientContext* context, const ::Empty* request, ::GameState* response, ::grpc::ClientUnaryReactor* reactor) {
  ::grpc::internal::ClientCallbackUnaryFactory::Create< ::grpc::protobuf::MessageLite, ::grpc::protobuf::MessageLite>(stub_->channel_.get(), stub_->rpcmethod_GetLastGameState_, context, request, response, reactor);
}

::grpc::ClientAsyncResponseReader< ::GameState>* Game::Stub::PrepareAsyncGetLastGameStateRaw(::grpc::ClientContext* context, const ::Empty& request, ::grpc::CompletionQueue* cq) {
  return ::grpc::internal::ClientAsyncResponseReaderHelper::Create< ::GameState, ::Empty, ::grpc::protobuf::MessageLite, ::grpc::protobuf::MessageLite>(channel_.get(), cq, rpcmethod_GetLastGameState_, context, request);
}

::grpc::ClientAsyncResponseReader< ::GameState>* Game::Stub::AsyncGetLastGameStateRaw(::grpc::ClientContext* context, const ::Empty& request, ::grpc::CompletionQueue* cq) {
  auto* result =
    this->PrepareAsyncGetLastGameStateRaw(context, request, cq);
  result->StartCall();
  return result;
}

Game::Service::Service() {
  AddMethod(new ::grpc::internal::RpcServiceMethod(
      Game_method_names[0],
      ::grpc::internal::RpcMethod::NORMAL_RPC,
      new ::grpc::internal::RpcMethodHandler< Game::Service, ::Empty, ::GameMeta, ::grpc::protobuf::MessageLite, ::grpc::protobuf::MessageLite>(
          [](Game::Service* service,
             ::grpc::ServerContext* ctx,
             const ::Empty* req,
             ::GameMeta* resp) {
               return service->GetGameMeta(ctx, req, resp);
             }, this)));
  AddMethod(new ::grpc::internal::RpcServiceMethod(
      Game_method_names[1],
      ::grpc::internal::RpcMethod::NORMAL_RPC,
      new ::grpc::internal::RpcMethodHandler< Game::Service, ::GameMeta, ::Empty, ::grpc::protobuf::MessageLite, ::grpc::protobuf::MessageLite>(
          [](Game::Service* service,
             ::grpc::ServerContext* ctx,
             const ::GameMeta* req,
             ::Empty* resp) {
               return service->SetGameMeta(ctx, req, resp);
             }, this)));
  AddMethod(new ::grpc::internal::RpcServiceMethod(
      Game_method_names[2],
      ::grpc::internal::RpcMethod::NORMAL_RPC,
      new ::grpc::internal::RpcMethodHandler< Game::Service, ::Empty, ::Empty, ::grpc::protobuf::MessageLite, ::grpc::protobuf::MessageLite>(
          [](Game::Service* service,
             ::grpc::ServerContext* ctx,
             const ::Empty* req,
             ::Empty* resp) {
               return service->Reset(ctx, req, resp);
             }, this)));
  AddMethod(new ::grpc::internal::RpcServiceMethod(
      Game_method_names[3],
      ::grpc::internal::RpcMethod::NORMAL_RPC,
      new ::grpc::internal::RpcMethodHandler< Game::Service, ::GameState, ::GameState, ::grpc::protobuf::MessageLite, ::grpc::protobuf::MessageLite>(
          [](Game::Service* service,
             ::grpc::ServerContext* ctx,
             const ::GameState* req,
             ::GameState* resp) {
               return service->SuggestNextMove(ctx, req, resp);
             }, this)));
  AddMethod(new ::grpc::internal::RpcServiceMethod(
      Game_method_names[4],
      ::grpc::internal::RpcMethod::NORMAL_RPC,
      new ::grpc::internal::RpcMethodHandler< Game::Service, ::Empty, ::GameState, ::grpc::protobuf::MessageLite, ::grpc::protobuf::MessageLite>(
          [](Game::Service* service,
             ::grpc::ServerContext* ctx,
             const ::Empty* req,
             ::GameState* resp) {
               return service->GetLastGameState(ctx, req, resp);
             }, this)));
}

Game::Service::~Service() {
}

::grpc::Status Game::Service::GetGameMeta(::grpc::ServerContext* context, const ::Empty* request, ::GameMeta* response) {
  (void) context;
  (void) request;
  (void) response;
  return ::grpc::Status(::grpc::StatusCode::UNIMPLEMENTED, "");
}

::grpc::Status Game::Service::SetGameMeta(::grpc::ServerContext* context, const ::GameMeta* request, ::Empty* response) {
  (void) context;
  (void) request;
  (void) response;
  return ::grpc::Status(::grpc::StatusCode::UNIMPLEMENTED, "");
}

::grpc::Status Game::Service::Reset(::grpc::ServerContext* context, const ::Empty* request, ::Empty* response) {
  (void) context;
  (void) request;
  (void) response;
  return ::grpc::Status(::grpc::StatusCode::UNIMPLEMENTED, "");
}

::grpc::Status Game::Service::SuggestNextMove(::grpc::ServerContext* context, const ::GameState* request, ::GameState* response) {
  (void) context;
  (void) request;
  (void) response;
  return ::grpc::Status(::grpc::StatusCode::UNIMPLEMENTED, "");
}

::grpc::Status Game::Service::GetLastGameState(::grpc::ServerContext* context, const ::Empty* request, ::GameState* response) {
  (void) context;
  (void) request;
  (void) response;
  return ::grpc::Status(::grpc::StatusCode::UNIMPLEMENTED, "");
}

