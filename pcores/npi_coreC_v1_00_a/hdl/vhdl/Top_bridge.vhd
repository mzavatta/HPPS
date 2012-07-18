----------------------------------------------------------------------------------------------------------------------------
-- Filename:        npi.vhd
-- Description:     Statemachine that controls the data transference between the NPI memory controller and the 
-- 					  peripheral. It sends and receives burst transferences from/to external memories using the NPI
--                  bus, and receives/sends DATA from external FIFOs, when required, using the included Control signals.
--                  
-- VHDL-Standard:   VHDL'93
-----------------------------------------------------------------------------------------------------------------------------
--------------------------------- LIBRARIES ---------------------------------------------------------------------------------
library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_unsigned.all;
use ieee.std_logic_arith.all;
-----------------------------------------------------------------------------------------------------------------------------

entity TOP_bridge is

  generic(
		C_PI_ADDR_WIDTH				: 	  integer						 := 32;												
		C_PI_DATA_WIDTH				: 	  integer						 := 64;											
		C_PI_BE_WIDTH					: 	  integer						 := 8;									
		C_PI_RDWDADDR_WIDTH			: 	  integer						 := 8;									
		ADDR_WIDTH						: 	  integer						 := 32;									 
		DATA_WIDTH						: 	  integer						 := 64;									  
		INITIAL_ADDRESS_RANGE      :     std_logic_vector(31 downto 0)	 	:= X"00000000";                               
		FINAL_ADDRESS_RANGE		   :     std_logic_vector(31 downto 0)	 	:= X"0000FFFF";                          
		BURST_LENGTH					:     std_logic_vector(3 downto 0)		:= "0000"
		);	
	 
  port(
	CLK									: in std_logic;
	RESET									: in std_logic;
	
	DEBUG_EI								: out std_logic_vector(5 downto 0);
	debug_NPI_controller_state    : out std_logic_vector(3 downto 0);
	debug_Wr_FIFO_Write_NPI			: out std_logic;
	debug_Wr_FIFO_DATA_NPI  		: out std_logic_vector(63 downto 0);
	debug_READ_DATA					: out std_logic_vector(63 downto 0);
	debug_Finish_transaction_REG	: out std_logic;
	debug_fifo_empty					: out std_logic;
	debug_READ_DATA_1				   : out std_logic_vector(DATA_WIDTH-1 downto 0);
	debug_S_in_size_REG				: out std_logic_vector(7 downto 0);
	debug_S_in_addr_REG				: out std_logic_vector(ADDR_WIDTH-1 downto 0);
	debug_Size_IN						: out std_logic_vector(7 downto 0);
	
	
	-- Input Chain Interface
	S_in_addr							: in std_logic_vector(ADDR_WIDTH-1 downto 0);
	S_in_size							: in std_logic_vector(7 downto 0);
	S_in_data_w							: in std_logic_vector(DATA_WIDTH-1 downto 0);
	S_in_LOAD							: in std_logic;
	S_in_STORE							: in std_logic;
	
	
	-- Output Chain Interface
	S_out_addr							: out std_logic_vector(ADDR_WIDTH-1 downto 0);
	S_out_size							: out std_logic_vector(7 downto 0);
	S_out_data_w						: out std_logic_vector(DATA_WIDTH-1 downto 0);
	S_out_data_r						: out std_logic_vector(DATA_WIDTH-1 downto 0);
	S_out_ready							: out std_logic;
	S_out_LOAD							: out std_logic;
	S_out_STORE							: out std_logic;
	
	    -- MPMC Port Interface - Bus is prefixed with NPI_ . Outputs Directly connected to the MPMC
    XIL_NPI_Addr              : out std_logic_vector(C_PI_ADDR_WIDTH-1 downto 0)     := (others => '0');
    XIL_NPI_AddrReq           : out std_logic                                        := '0';
    XIL_NPI_AddrAck           : in  std_logic                                        := '0';
    XIL_NPI_RNW               : out std_logic                                        := '0';
    XIL_NPI_Size              : out std_logic_vector(3 downto 0)                     := (others => '0');
    XIL_NPI_WrFIFO_Data       : out std_logic_vector(C_PI_DATA_WIDTH-1 downto 0)     := (others => '0');
    XIL_NPI_WrFIFO_BE         : out std_logic_vector(C_PI_BE_WIDTH-1 downto 0)       := (others => '0');
    XIL_NPI_WrFIFO_Push       : out std_logic                                        := '0';
    XIL_NPI_RdFIFO_Data       : in  std_logic_vector(C_PI_DATA_WIDTH-1 downto 0)     := (others => '0');
    XIL_NPI_RdFIFO_Pop        : out std_logic                                        := '0';
    XIL_NPI_RdFIFO_RdWdAddr   : in  std_logic_vector(C_PI_RDWDADDR_WIDTH-1 downto 0) := (others => '0');
    XIL_NPI_WrFIFO_Empty      : in  std_logic                                        := '0';
    XIL_NPI_WrFIFO_AlmostFull : in  std_logic                                        := '0';
    XIL_NPI_WrFIFO_Flush      : out std_logic                                        := '0';
    XIL_NPI_RdFIFO_Empty      : in  std_logic                                        := '0';
    XIL_NPI_RdFIFO_Flush      : out std_logic                                        := '0';
    XIL_NPI_RdFIFO_Latency    : in  std_logic_vector(1 downto 0)                     := (others => '0');
    XIL_NPI_RdModWr           : out std_logic                                        := '0';
    XIL_NPI_InitDone          : in  std_logic                                        := '0';
    XIL_NPI_Clk               : in  std_logic                                        := '0';
    XIL_NPI_Rst               : in  std_logic                                        := '0'
	);

end entity;


architecture structural of TOP_bridge is 
component External_interface is

  generic(
		ADDR_WIDTH						: 	  integer								:= 32;
		DATA_WIDTH						: 	  integer								:= 32;
		INITIAL_ADDRESS_RANGE      :     std_logic_vector(31 downto 0)	:= X"FFFF0000";
		FINAL_ADDRESS_RANGE		   :     std_logic_vector(31 downto 0)	:= X"FFFFFFFF";
		BURST_LENGTH					:     std_logic_vector(3 downto 0)	:= "0101" );
	 
  port(
	CLK									: in std_logic;
	RESET									: in std_logic;
	
	DEBUG_EI								: out std_logic_vector(5 downto 0);
	debug_READ_DATA_1				   : out std_logic_vector(DATA_WIDTH-1 downto 0);
	debug_S_in_size_REG				: out std_logic_vector(7 downto 0);
	debug_S_in_addr_REG				: out std_logic_vector(ADDR_WIDTH-1 downto 0);
	
	--- NPI Interface
	INSTRUCTION							: out std_logic_vector(1 downto 0);
	READ_DATA							: in std_logic_vector(DATA_WIDTH-1 downto 0);
	IN_READY								: in std_logic;
	IN_READY_load						: in std_logic;
	WRITE_DATA							: out std_logic_vector(DATA_WIDTH-1 downto 0);
	OUTPUT_ADDRESS						: out std_logic_vector(ADDR_WIDTH-1 downto 0);
	npi_wrfifo_be						: out std_logic_vector(7 downto 0);
	
	-- Input Chain Interface
	S_in_addr							: in std_logic_vector(ADDR_WIDTH-1 downto 0);
	S_in_size							: in std_logic_vector(7 downto 0);
	S_in_data_w							: in std_logic_vector(DATA_WIDTH-1 downto 0);
	S_in_LOAD							: in std_logic;
	S_in_STORE							: in std_logic;
	
	
	-- Output Chain Interface
	S_out_addr							: out std_logic_vector(ADDR_WIDTH-1 downto 0);
	S_out_size							: out std_logic_vector(7 downto 0);
	S_out_data_w						: out std_logic_vector(DATA_WIDTH-1 downto 0);
	S_out_data_r						: out std_logic_vector(DATA_WIDTH-1 downto 0);
	S_out_ready							: out std_logic;
	S_out_LOAD							: out std_logic;
	S_out_STORE							: out std_logic);
  
end component;

component my_npi is

  generic(
		C_PI_ADDR_WIDTH       	:     integer                                      := 32;
		C_PI_DATA_WIDTH       	:     integer                                      := 64;
		ADDR_WIDTH					: 	   integer													:= 32;
		DATA_WIDTH					: 	   integer													:= 32;
		C_PI_BE_WIDTH         	:     integer                                      := 8;
		C_PI_RDWDADDR_WIDTH   	:     integer                                      := 4;
		BURST_LENGTH				:     std_logic_vector(3 downto 0)						:= "0101" );
	 
  port(
	 -- Debug Signals ---------------------------------------------------
	 debug_NPI_controller_state    	: out std_logic_vector(3 downto 0);

	 --------------------------------------------------------------------
	 
    -- User interface signals
		-- Begin/End signals (External Commands)
	 SendDataBegin					: in std_logic;
	 ReceiveDataBegin				: in std_logic;
	 Finish_transaction_NPI		: out std_logic;
	 
	 npi_wrfifo_be_in				: in std_logic_vector(7 downto 0);
	 
		-- Memory Address  -- Destination Address. Has to be Updated externaly
	 Memory_Address				: in std_logic_vector(C_PI_ADDR_WIDTH-1 downto 0);
	 
	 -- Read Data signals (Read Data from an output FIFO)
	 Rd_FIFO_DATA				: in std_logic_vector(C_PI_DATA_WIDTH-1 downto 0) ;
	 Rd_FIFO_Request			: out std_logic;
	 data_read_valid 			: in std_logic;
	 
	 -- Write Data signals (Sended to an output FIFO)
	 Wr_FIFO_DATA				: out std_logic_vector(C_PI_DATA_WIDTH-1 downto 0);
	 Wr_FIFO_Write				: out std_logic;

    -- MPMC Port Interface - Bus is prefixed with NPI_ . Outputs Directly connected to the MPMC
    XIL_NPI_Addr              : out std_logic_vector(C_PI_ADDR_WIDTH-1 downto 0)     := (others => '0');
    XIL_NPI_AddrReq           : out std_logic                                        := '0';
    XIL_NPI_AddrAck           : in  std_logic                                        := '0';
    XIL_NPI_RNW               : out std_logic                                        := '0';
    XIL_NPI_Size              : out std_logic_vector(3 downto 0)                     := (others => '0');
    XIL_NPI_WrFIFO_Data       : out std_logic_vector(C_PI_DATA_WIDTH-1 downto 0)     := (others => '0');
    XIL_NPI_WrFIFO_BE         : out std_logic_vector(C_PI_BE_WIDTH-1 downto 0)       := (others => '0');
    XIL_NPI_WrFIFO_Push       : out std_logic                                        := '0';
    XIL_NPI_RdFIFO_Data       : in  std_logic_vector(C_PI_DATA_WIDTH-1 downto 0)     := (others => '0');
    XIL_NPI_RdFIFO_Pop        : out std_logic                                        := '0';
    XIL_NPI_RdFIFO_RdWdAddr   : in  std_logic_vector(C_PI_RDWDADDR_WIDTH-1 downto 0) := (others => '0');
    XIL_NPI_WrFIFO_Empty      : in  std_logic                                        := '0';
    XIL_NPI_WrFIFO_AlmostFull : in  std_logic                                        := '0';
    XIL_NPI_WrFIFO_Flush      : out std_logic                                        := '0';
    XIL_NPI_RdFIFO_Empty      : in  std_logic                                        := '0';
    XIL_NPI_RdFIFO_Flush      : out std_logic                                        := '0';
    XIL_NPI_RdFIFO_Latency    : in  std_logic_vector(1 downto 0)                     := (others => '0');
    XIL_NPI_RdModWr           : out std_logic                                        := '0';
    XIL_NPI_InitDone          : in  std_logic                                        := '0';
    XIL_NPI_Clk               : in  std_logic                                        := '0';
    XIL_NPI_Rst               : in  std_logic                                        := '0');
	 
end component;


component FIFO_2_CLKS
	port (
	rst: IN std_logic;
	wr_clk: IN std_logic;
	rd_clk: IN std_logic;
	din: IN std_logic_VECTOR(63 downto 0);
	wr_en: IN std_logic;
	rd_en: IN std_logic;
	dout: OUT std_logic_VECTOR(63 downto 0);
	full: OUT std_logic;
	almost_full: OUT std_logic;
	wr_ack: OUT std_logic;
	empty: OUT std_logic;
	almost_empty: OUT std_logic;
	valid: OUT std_logic);
end component;

	signal INSTRUCTION								: std_logic_vector(1 downto 0);
	signal READ_DATA									: std_logic_vector(DATA_WIDTH-1 downto 0);
	signal IN_READY									: std_logic;
	signal WRITE_DATA									: std_logic_vector(DATA_WIDTH-1 downto 0);
	signal OUTPUT_ADDRESS							: std_logic_vector(ADDR_WIDTH-1 downto 0);
	signal SendDataBegin								: std_logic;
	signal ReceiveDataBegin							: std_logic;
	signal Finish_transaction_NPI					: std_logic;
	signal Finish_transaction_REG					: std_logic;
	signal Memory_Address							: std_logic_vector(C_PI_ADDR_WIDTH-1 downto 0);
	signal Rd_FIFO_DATA_NPI							: std_logic_vector(C_PI_DATA_WIDTH-1 downto 0) ;
	signal Rd_FIFO_Request_NPI						: std_logic;
	signal data_read_valid_NPI 					: std_logic;
	signal Wr_FIFO_DATA_NPI							: std_logic_vector(C_PI_DATA_WIDTH-1 downto 0);
	signal Wr_FIFO_Write_NPI						: std_logic;
	--signal debug_NPI_controller_state  			: std_logic_vector(3 downto 0);
	signal IN_READY_load 							: std_logic;
	signal Finish_transaction_REG1, Finish_transaction_REG2, Finish_transaction_REG3, Finish_transaction_REG4, Finish_transaction_REG5, Finish_transaction_REG6, Finish_transaction_REG7 : std_logic;
	
	signal npi_wrfifo_be_int						: std_logic_vector(7 downto 0);
	
begin


	-- External 
BusChain:  External_interface
  generic map(
		ADDR_WIDTH						=> ADDR_WIDTH,
		DATA_WIDTH						=> DATA_WIDTH,
		INITIAL_ADDRESS_RANGE      => INITIAL_ADDRESS_RANGE,
		FINAL_ADDRESS_RANGE		  	=> FINAL_ADDRESS_RANGE,
		BURST_LENGTH					=> BURST_LENGTH)
	 
  port map(
	CLK									=> CLK,
	RESET									=> RESET,
	
	DEBUG_EI								=> DEBUG_EI,
	debug_READ_DATA_1					=> debug_READ_DATA_1,
	debug_S_in_size_REG				=> debug_S_in_size_REG,
	debug_S_in_addr_REG				=> debug_S_in_addr_REG,
	
	--- NPI Interface
	INSTRUCTION							=> INSTRUCTION,
	READ_DATA							=> READ_DATA,
	IN_READY_load						=> IN_READY_load,
	IN_READY								=> IN_READY,
	WRITE_DATA							=> WRITE_DATA,
	OUTPUT_ADDRESS						=> OUTPUT_ADDRESS,
	npi_wrfifo_be						=> npi_wrfifo_be_int,
	
	-- Input Chain Interface
	S_in_addr							=> S_in_addr,
	S_in_size							=> S_in_size,
	S_in_data_w							=> S_in_data_w,
	S_in_LOAD							=> S_in_LOAD,
	S_in_STORE							=> S_in_STORE,
	
	
	-- Output Chain Interface
	S_out_addr							=> S_out_addr,
	S_out_size							=> S_out_size,
	S_out_data_w						=> S_out_data_w,
	S_out_data_r						=> S_out_data_r,
	S_out_ready							=> S_out_ready,
	S_out_LOAD							=> S_out_LOAD,
	S_out_STORE							=> S_out_STORE

	);
	
	---- CROSSING CLOCK DOMAIN FIFOs -----------------------------------------
	
	---------- STORE operation FIFO ----------------------
	 store_fifo: FIFO_2_CLKS
		port map (
			rst => RESET,
			wr_clk => CLK,
			rd_clk => XIL_NPI_Clk,
			din => WRITE_DATA,
			wr_en => INSTRUCTION(1),
			rd_en => Rd_FIFO_Request_NPI,
			dout => Rd_FIFO_DATA_NPI,
			full => open,
			almost_full => open,
			wr_ack => open,
			empty => open,
			almost_empty => open,
			valid => data_read_valid_NPI);
			
			
			
			
	 ----- LOAD operation FIFO
	 load_fifo : FIFO_2_CLKS
		port map (
			rst => RESET,
			wr_clk => XIL_NPI_Clk,
			rd_clk => CLK,
			din => Wr_FIFO_DATA_NPI, -- este
			wr_en => Wr_FIFO_Write_NPI, --este
			rd_en => Finish_transaction_REG,
			dout => READ_DATA,
			full => open,
			almost_full => open,
			wr_ack => open,
			empty => debug_fifo_empty,
			almost_empty => open,
			valid => IN_READY_load);

	--debug_Finish_transaction_REG			<= Finish_transaction_REG;
	debug_Wr_FIFO_Write_NPI					<= Wr_FIFO_Write_NPI;
	debug_Wr_FIFO_DATA_NPI  				<= Wr_FIFO_DATA_NPI;
	--debug_READ_DATA							<= READ_DATA;

	--debug_Wr_FIFO_DATA_NPI  				<= WRITE_DATA;
	debug_READ_DATA							<= READ_DATA;
	
	
	debug_Finish_transaction_REG			<= Finish_transaction_REG;
	--debug_Wr_FIFO_Write_NPI					<=  INSTRUCTION(1);

		IN_READY <= (Finish_transaction_REG); 

	----------------------------------------------------------------------------
	
	--------------------- CROSSING CLOCK DOMAIN COMMANDS -----------------------
	
		-- From XIL_NPI_Clk to CLK (CLOCK EXTENSION??)
		process(CLK)
		begin
			if (CLK'event and CLK = '1') then
				Finish_transaction_REG <= Finish_transaction_REG7;
				Finish_transaction_REG7 <= Finish_transaction_REG6;
				Finish_transaction_REG6 <= Finish_transaction_REG5;
				Finish_transaction_REG5 <= Finish_transaction_REG4;
				Finish_transaction_REG4 <= Finish_transaction_REG3;
				Finish_transaction_REG3 <= Finish_transaction_REG2;
				Finish_transaction_REG2 <= Finish_transaction_REG1;
				Finish_transaction_REG1 <= Finish_transaction_NPI;
			end if;
		end process;
		
		-- From CLK to XIL_NPI_Clk
		
		process(XIL_NPI_Clk)
		begin
			if (XIL_NPI_Clk'event and XIL_NPI_Clk = '1') then
				SendDataBegin		<= INSTRUCTION(1);
				ReceiveDataBegin 	<= INSTRUCTION(0); 
	     
				Memory_Address      <= OUTPUT_ADDRESS;
			end if;
		 end process;
		 		
	-----------------------------------------------------------------------------
	
  
NPI_interface: my_npi

  generic map(
		C_PI_ADDR_WIDTH       	=> C_PI_ADDR_WIDTH,
		C_PI_DATA_WIDTH       	=> C_PI_DATA_WIDTH,
		ADDR_WIDTH					=> ADDR_WIDTH,
		DATA_WIDTH					=> DATA_WIDTH,
		C_PI_BE_WIDTH         	=> C_PI_BE_WIDTH,
		C_PI_RDWDADDR_WIDTH   	=> C_PI_RDWDADDR_WIDTH,
		BURST_LENGTH			   => "0000" )
	 
  port map(
	 -- Debug Signals ---------------------------------------------------
	 debug_NPI_controller_state    	=>  debug_NPI_controller_state, 
	 --------------------------------------------------------------------
	 
    -- User interface signals
		-- Begin/End signals (External Commands)
	 SendDataBegin					 	=> SendDataBegin, 
	 ReceiveDataBegin				 	=> ReceiveDataBegin, 
	 Finish_transaction_NPI			=> Finish_transaction_NPI, 
	 npi_wrfifo_be_in					=> npi_wrfifo_be_int,
	 
		-- Memory Address  -- Destination Address. Has to be Updated externaly
	 Memory_Address				=>  Memory_Address, 
	 
	 -- Read Data signals (Read Data from an output FIFO)
	 Rd_FIFO_DATA				 	=> Rd_FIFO_DATA_NPI, 
	 Rd_FIFO_Request			 	=> Rd_FIFO_Request_NPI, 
	 data_read_valid 			 	=> data_read_valid_NPI, 
	 
	 -- Write Data signals (Sended to an output FIFO)
	 Wr_FIFO_DATA				 	=> Wr_FIFO_DATA_NPI, 
	 Wr_FIFO_Write				 	=> Wr_FIFO_Write_NPI, 

    -- MPMC Port Interface - Bus is prefixed with NPI_ . Outputs Directly connected to the MPMC
    XIL_NPI_Addr              => XIL_NPI_Addr,
    XIL_NPI_AddrReq           => XIL_NPI_AddrReq,
    XIL_NPI_AddrAck           => XIL_NPI_AddrAck,
    XIL_NPI_RNW               => XIL_NPI_RNW,
    XIL_NPI_Size              => XIL_NPI_Size,
    XIL_NPI_WrFIFO_Data       => XIL_NPI_WrFIFO_Data,
    XIL_NPI_WrFIFO_BE         => XIL_NPI_WrFIFO_BE,
    XIL_NPI_WrFIFO_Push       => XIL_NPI_WrFIFO_Push,
    XIL_NPI_RdFIFO_Data       => XIL_NPI_RdFIFO_Data,
    XIL_NPI_RdFIFO_Pop        => XIL_NPI_RdFIFO_Pop,
    XIL_NPI_RdFIFO_RdWdAddr   => XIL_NPI_RdFIFO_RdWdAddr,
    XIL_NPI_WrFIFO_Empty      => XIL_NPI_WrFIFO_Empty,
    XIL_NPI_WrFIFO_AlmostFull => XIL_NPI_WrFIFO_AlmostFull,
    XIL_NPI_WrFIFO_Flush      => XIL_NPI_WrFIFO_Flush,
    XIL_NPI_RdFIFO_Empty      => XIL_NPI_RdFIFO_Empty,
    XIL_NPI_RdFIFO_Flush      => XIL_NPI_RdFIFO_Flush,
    XIL_NPI_RdFIFO_Latency    => XIL_NPI_RdFIFO_Latency,
    XIL_NPI_RdModWr           => XIL_NPI_RdModWr,
    XIL_NPI_InitDone          => XIL_NPI_InitDone,
    XIL_NPI_Clk               => XIL_NPI_Clk,
    XIL_NPI_Rst               => XIL_NPI_Rst );

end architecture;