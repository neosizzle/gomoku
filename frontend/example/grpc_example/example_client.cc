// first, add the directory that contain all grpc.pc files into PKG_CONFIG_PATH
// export PKG_CONFIG_PATH="/home/nszl/42cursus/gomoku/frontend/grpc/lib/pkgconfig:$PKG_CONFIG_PATH"
// g++ example_client.cc game.*.cc -I . -I  ../../grpc/include/ -L/usr/local/lib -L../../grpc/lib `pkg-config --cflags --libs --static protobuf grpc grpc++  absl_flags absl_flags_parse` -o example_client

// in grpc.rc and grpc++.rc, re2 is removed because of https://github.com/grpc/grpc/issues/35260. It is replaced here instead
// re2.pc is added MANUALLY because  grpc.rc and grpc++.rc requires it but it is not provided in default installation https://github.com/grpc/grpc/issues/35260

#include <iostream>
#include <memory>
#include <string>
#include <thread>

#include "absl/flags/flag.h"
#include "absl/flags/parse.h"

#include <grpcpp/grpcpp.h>

#include "game.grpc.pb.h"
#include "game.pb.h"

ABSL_FLAG(std::string, target, "localhost:50051", "Server address");

using grpc::Channel;
using grpc::ClientContext;
using grpc::Status;

class GameClient {
	public:
		GameClient(std::shared_ptr<Channel> channel)
			: stub_(Game::NewStub(channel)) {}

		// Assembles the client's payload, sends it and presents the response back
		// from the server.
		GameState RunTask(GameState& request) {
			// Container for the data we expect from the server.
			GameState reply;

			// Context for the client. It could be used to convey extra information to
			// the server and/or tweak certain RPC behaviors.
			ClientContext context;

			// The actual RPC.
			Status status = stub_->SuggestNextMove(&context, request, &reply);
			
			return reply;
			// Act upon its status.
			// if (status.ok()) {
			// 	return reply.message();
			// } else {
			// 	std::cout << status.error_code() << ": " << status.error_message()
			// 			<< std::endl;
			// 	return "RPC failed";
			// }
		}

	private:
		std::unique_ptr<Game::Stub> stub_;
};

int main(int argc, char** argv) {
	absl::ParseCommandLine(argc, argv);
	// Instantiate the client. It requires a channel, out of which the actual RPCs
	// are created. This channel models a connection to an endpoint specified by
	// the argument "--target=" which is the only expected argument.
	std::string target_str = absl::GetFlag(FLAGS_target);
	// We indicate that the channel isn't authenticated (use of
	// InsecureChannelCredentials()).
	GameClient game(
		grpc::CreateChannel(target_str, grpc::InsecureChannelCredentials()));

	std::cout << "Server connected\n"; 
	GameState state;
	
	state.set_board(std::string(16, 0));

	while (1)
	{
		char const *board_bytes = state.board().c_str();
		for (size_t i = 0; i < 16; i++)
			std::cout << (int)board_bytes[i] << " ";	
		std::cout <<  "\n";
		state = game.RunTask(state);
		std::this_thread::sleep_for(std::chrono::seconds(1));
	}
	

	// std::string user("world");
	// std::string reply = game.SayHello(user);
	// std::cout << "Greeter received: " << reply << std::endl;

	return 0;
}
