FROM rust:1.87

WORKDIR /usr/src/myapp

COPY . .

RUN apt-get update && apt-get install -y dos2unix gdown 

RUN dos2unix libtorch_setup.sh

RUN bash ./libtorch_setup.sh

ENV LIBTORCH=/home/util/libtorch/libtorch
ENV LIBTORCH_INCLUDE=$LIBTORCH
ENV LIBTORCH_LIB=$LIBTORCH
ENV LD_LIBRARY_PATH=$LIBTORCH/lib:/usr/local/lib:/usr/lib

ENV DATABASE_URL=postgres://psqlx:psqlx@host.docker.internal:5432/uploads

RUN cargo install sqlx-cli

RUN sqlx migrate run

RUN cargo build

CMD ["./target/debug/back"]