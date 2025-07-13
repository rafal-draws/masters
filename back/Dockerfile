FROM rust:1.87

WORKDIR /usr/src/myapp

COPY . .

RUN apt-get update && apt-get install -y dos2unix 

RUN dos2unix libtorch_setup.sh

RUN bash ./libtorch_setup.sh

ENV LIBTORCH=/home/util/libtorch/libtorch

ENV LIBTORCH_INCLUDE=/home/util/libtorch/libtorch

ENV LIBTORCH_LIB=/home/util/libtorch/libtorch

ENV LD_LIBRARY_PATH=/home/util/libtorch/libtorch/lib:$LD_LIBRARY_PATH

RUN cargo install sqlx-cli

RUN sqlx migrate run

RUN cargo build

CMD ["./target/debug/back"]