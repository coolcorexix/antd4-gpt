{ pkgs, lib, config, ... }:
{
  process.implementation = "process-compose";
	env.TZ                  = "UTC";
	env.PGUSER              = "postgres";
  dotenv = {
    enable=true;
    filename=".env.development";
  };
  enterShell = ''
		echo $PGUSER >/tmp/password.txt
		initdb --username=$PGUSER --encoding=UTF-8 --locale=en_US.UTF-8 --auth=md5 --pwfile=/tmp/password.txt
		rm /tmp/password.txt
		mkdir -p "$PGDATA/run" "$PGDATA/logs"
		sed -i -e "s@#unix_socket_directories  *=  *.*@unix_socket_directories = '$PGDATA/run'@" $PGDATA/postgresql.conf
		pg_ctl --log $PGDATA/logs/postgres.log start
		echo "Postgres started"
  '';
  services ={
    postgres = {
      enable = true;
      package = pkgs.postgresql_15;
      settings = {
        "log_error_verbosity" = "VERBOSE";
      };
      initialDatabases = [
            { name = "postgres";}
            { name = "ant4-gpt";}
      ];
      port = lib.toInt config.env.POSTGRES_PORT;
      listen_addresses=config.env.POSTGRES_HOST_ADDRESS;

    };
  };
}