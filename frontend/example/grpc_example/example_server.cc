// first, add the directory that contain all grpc.pc files into PKG_CONFIG_PATH
// export PKG_CONFIG_PATH="/home/nszl/42cursus/gomoku/frontend/grpc/lib/pkgconfig:$PKG_CONFIG_PATH"
// g++ example_server.cc game.*.cc -I . -I  ../../grpc/include/ -lgrpc++_reflection -L/usr/local/lib -L../../grpc/lib `pkg-config --cflags --libs --static protobuf grpc grpc++  absl_flags absl_flags_parse` -o example_server

// in grpc.rc and grpc++.rc, re2 is removed because of https://github.com/grpc/grpc/issues/35260. It is replaced here instead
// re2.pc is added MANUALLY because  grpc.rc and grpc++.rc requires it but it is not provided in default installation https://github.com/grpc/grpc/issues/35260
#include "game.grpc.pb.h"
#include "game.pb.h"

#include "absl/flags/flag.h"
#include "absl/flags/parse.h"
#include "absl/strings/str_format.h"

#include <grpcpp/ext/proto_server_reflection_plugin.h>
#include <grpcpp/grpcpp.h>
#include <grpcpp/health_check_service_interface.h>

using grpc::Server;
using grpc::ServerBuilder;
using grpc::ServerContext;
using grpc::Status;

// argv option
ABSL_FLAG(uint16_t, port, 50051, "Server port for the service");

// Logic and data behind the server's behavior.
class GameServiceImpl final : public Game::Service {
	private:
		bool _initialized;
		int game_id;
		ModeType mode;
		int grid_size;
	Status GetGameMeta(ServerContext *context, const Empty* _empty, GameMeta* ret) override
	{
		ret->set__initialized(this->_initialized);
		ret->set_gameid(this->game_id);
		ret->set_mode(this->mode);
		ret->set_gridsize(this->grid_size);
		return Status::OK;
	}

	Status SetGameMeta(ServerContext *context, const GameMeta* meta, Empty* _empty) override
	{
		this->_initialized = meta->_initialized();
		this->game_id = meta->gameid();
		this->mode = meta->mode();
		this->grid_size = meta->gridsize();

		return Status::OK;
	}

	Status Reset(ServerContext *context, const Empty* _empty, Empty* _empty2) override
	{
		return Status::OK;
	}

	Status SuggestNextMove(ServerContext *context, const GameState* req, GameState* res) override
	{
		std::string new_buffer(req->board());
		new_buffer[0] += 1;

		res->set_board(new_buffer);
		return Status::OK;
	}

	public:
		GameServiceImpl() : _initialized(false), game_id(0), mode(ModeType::PVP_PRO), grid_size(4) {}
};

void RunServer(uint16_t port) {
	std::string server_address = absl::StrFormat("0.0.0.0:%d", port);
	GameServiceImpl service;

	grpc::EnableDefaultHealthCheckService(true);
	grpc::reflection::InitProtoReflectionServerBuilderPlugin();
	ServerBuilder builder;
	// Listen on the given address without any authentication mechanism.
	builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());
	// Register "service" as the instance through which we'll communicate with
	// clients. In this case it corresponds to an *synchronous* service.
	builder.RegisterService(&service);
	// Finally assemble the server.
	std::unique_ptr<Server> server(builder.BuildAndStart());
	std::cout << "Server listening on " << server_address << std::endl;

	// Wait for the server to shutdown. Note that some other thread must be
	// responsible for shutting down the server for this call to ever return.
	server->Wait();
}

int main(int argc, char *argv[])
{
	absl::ParseCommandLine(argc, argv);
	uint16_t port = absl::GetFlag(FLAGS_port);
	RunServer(port);
	return 0;
}
