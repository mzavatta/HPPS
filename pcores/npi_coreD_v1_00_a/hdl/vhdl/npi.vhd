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
entity my_npi is

  generic(
		C_PI_ADDR_WIDTH       	:     integer                                      := 32;
		C_PI_DATA_WIDTH       	:     integer                                      := 64;
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
	 
end entity;



architecture arc_my_npi of my_npi is

  type state_type is (RST, IDLE, TX_DATA, TX_ADDR, RX_ADDR, RX_WAIT_NOT_EMPTY,
                      RX_WAIT_RXFIFO_LAT2, RX_WAIT_RXFIFO_LAT1, RX_POP, IDLE_P);	 
  signal npi_cs, npi_ns    : state_type;
  
  
  signal npi_wrfifo_push_i : std_logic                                    := '0';
  signal npi_req_set       : std_logic                                    := '0';
  signal npi_rnw_i         : std_logic                                    := '0';
  signal npi_wrfifo_be_i   : std_logic_vector(C_PI_BE_WIDTH-1 downto 0)   := (others => '0');
  signal npi_size_i        : std_logic_vector(3 downto 0)                 := (others => '0');
  signal npi_addrreq_int   : std_logic                                    := '0';
  signal initdone          : std_logic                                    := '0';
  signal npi_rdfifo_pop_i  : std_logic                                    := '0';
  
  -- Pipelining signals
  signal XIL_NPI_WrFIFO_Data_internal, XIL_NPI_WrFIFO_Data_internal_1: std_logic_vector(63 downto 0);
  signal data_read_valid_reg: std_logic;
  signal  Memory_Address_REG				: std_logic_vector(C_PI_ADDR_WIDTH-1 downto 0);

	 begin
	 
		----------------- debug signals ---------------------
					
			 debug_NPI_controller_state <= 	 "1111" when npi_cs = RST else
														 "0001" when npi_cs = IDLE else
														 "0010" when npi_cs = TX_DATA else
														 "0011" when npi_cs = TX_ADDR else
														 "0100" when npi_cs = RX_ADDR else
														 "0101" when npi_cs = RX_WAIT_NOT_EMPTY else
														 "0110" when npi_cs = RX_WAIT_RXFIFO_LAT2 else
														 "0111" when npi_cs = RX_WAIT_RXFIFO_LAT1 else
														 "1000" when npi_cs = RX_POP else
														 "1001" when npi_cs = IDLE_P  else
														 "0000";
							
							
		--------------------- OUTPUTS -------------------------------
			-- MPMC Signal assignment
			XIL_NPI_WrFIFO_Flush  <= '0';
			XIL_NPI_RdFIFO_Flush  <= '0';  
			XIL_NPI_RdFIFO_Pop 	 <= npi_rdfifo_pop_i;
			XIL_NPI_AddrReq    	 <= npi_addrreq_int;
		  
			 -- Data assignment
			Wr_FIFO_DATA 			<= XIL_NPI_RdFIFO_Data;
			XIL_NPI_WrFIFO_Data 	<= XIL_NPI_WrFIFO_Data_internal; 
		--------------------------------------------------------------
				
		-- Basic pipeline for write path signals
		  PIPE         : process (XIL_NPI_Clk)
		  begin
			 if rising_edge(XIL_NPI_Clk) then
				initdone        						<= XIL_NPI_InitDone;
				XIL_NPI_WrFIFO_Push 					<= npi_wrfifo_push_i;
				XIL_NPI_WrFIFO_BE   					<= npi_wrfifo_be_i;
				XIL_NPI_WrFIFO_Data_internal_1 	<= Rd_FIFO_DATA;
				XIL_NPI_WrFIFO_Data_internal 		<= XIL_NPI_WrFIFO_Data_internal_1;
				data_read_valid_reg  				<= data_read_valid; 
			 end if;
		  end process;

		  
		  -- Upon address ack, clear address qualifiers 
		  ADDRACK_PIPE : process (XIL_NPI_Clk, XIL_NPI_AddrAck)
		  begin
			 if rising_edge(XIL_NPI_Clk) then
				if XIL_NPI_AddrAck = '1' then
				  XIL_NPI_RNW       <= '0';
				  XIL_NPI_Size      <= BURST_LENGTH;
				else
				  XIL_NPI_RNW       <= npi_rnw_i;
				  XIL_NPI_Size      <= npi_size_i;
				end if;
			 end if;
		  end process;

		  -- Address ack pipeline / Deassert address request 
		  NPI_REQ_PIPE : process (XIL_NPI_Clk, XIL_NPI_AddrAck, npi_req_set)
		  begin
			 if rising_edge(XIL_NPI_Clk) then
				if XIL_NPI_AddrAck = '1' then
				  npi_addrreq_int <= '0';
				elsif npi_req_set = '1' then
				  npi_addrreq_int <= '1';
				else
				  npi_addrreq_int <= npi_addrreq_int;
				end if;
			 end if;
		  end process;
		  
		  -- Address Register
		  ADDRSS_REG : process (XIL_NPI_Clk,XIL_NPI_Rst)
		  begin
			if (XIL_NPI_Rst = '1') then 	
				Memory_Address_REG <= (others => '0');
			elsif rising_edge(XIL_NPI_Clk) then
				if ((SendDataBegin = '1') or (ReceiveDataBegin = '1')) then
				  Memory_Address_REG <= Memory_Address;
				else
				  Memory_Address_REG <= Memory_Address_REG;
				end if;
			 end if;
		  end process;
		  
		  npi_wrfifo_be_i <= npi_wrfifo_be_in;
		  
		-----------------------------------------------------
		  -- STATE MACHINE THAT CONTROLS DATA TRANSFERENCE
		  NPI_STATE_NS : process (npi_cs,ReceiveDataBegin,SendDataBegin , XIL_NPI_AddrAck, XIL_NPI_RdFIFO_Latency, XIL_NPI_RdFIFO_Empty, data_read_valid_reg,Memory_Address_REG)
		  begin
		  
			 --default signal values if not overriden by current state
			 npi_ns                  <= npi_cs;
			 npi_wrfifo_push_i       <= '0';
			 npi_rdfifo_pop_i   		 <= '0';
			 npi_req_set             <= '0';
			 npi_rnw_i               <= '0';
			 npi_size_i              <= "0000";
			 
			 Finish_transaction_NPI  <= '0';
			 Wr_FIFO_Write				 <= '0';
			 Rd_FIFO_Request     	 <= '0';

			 case (npi_cs) is
				 when RST     =>
					 -- Reset State
					 
					 npi_ns            <= IDLE; 
				
				 when IDLE  =>
					 -- IDLE State
					
					 if (SendDataBegin = '1') then
					 -- Send Data
					
						 npi_ns              <= TX_ADDR;
						
						 -- Data is requested to the FIFO.
						 npi_req_set        	<= '1';
						 npi_rnw_i           <= '0';

						 XIL_NPI_Addr 		   <= Memory_Address_REG;
							 
					 elsif(ReceiveDataBegin = '1') then
					 -- Receive Data
				  
						 npi_ns             <= RX_ADDR;
					 
						 npi_req_set        	<= '1';
						 npi_rnw_i          	<= '1';	 
						
						 XIL_NPI_Addr 		<= Memory_Address_REG;
					 
					 else 
					
						npi_req_set        	<= '0';
						npi_rnw_i            <= '0';
						 
						npi_ns             <= IDLE;
					 
					 end if;
					 
				  when TX_ADDR  =>
				 -- Address Transmission
					
					 XIL_NPI_Addr 		<= Memory_Address_REG;
					 npi_size_i       <= "0000";
					 npi_rnw_i        <= '0'; 
				  
					 if XIL_NPI_AddrAck = '1' then
					
						 npi_ns              	<= TX_DATA;
						 npi_req_set        		<= '0'; 
						 Rd_FIFO_Request    		<= '1'; 

					 else
				  
						 npi_ns             <= TX_ADDR;
						 npi_req_set        <= '1';
						 Rd_FIFO_Request    <= '0'; 

					 end if;
					 
				 when TX_DATA =>
					 -- Data transmission to the memory

					 Rd_FIFO_Request     <= '0';  
					 
					 npi_req_set  <= '0';
					 npi_rnw_i    <= '0';
					 npi_size_i   <= "0000";
					 
					 XIL_NPI_Addr <= X"00000000";
					 
					 -- Increase the counter, only when data is valid.
					 if (data_read_valid_reg = '1') then 
					
						 -- Continue to push data into WrFIFO
						 npi_wrfifo_push_i  	<= '1';   
						 
						 npi_ns       					<= IDLE;
						 Finish_transaction_NPI  	<= '1';
						
					 else

						 npi_wrfifo_push_i  		<= '0';
						 
						 npi_ns      			 		<= TX_DATA;
						 Finish_transaction_NPI  	<= '0';

					 end if;
				 
				  
				 when RX_ADDR  =>
					 -- Start read, which starts with the address phase first
				 
					 XIL_NPI_Addr 		  <= Memory_Address_REG;
					 npi_size_i         <= "0000";
						 
					 if XIL_NPI_AddrAck = '1' then
					 
						 npi_ns             <= RX_WAIT_NOT_EMPTY;
						 npi_req_set        <= '0';
						 npi_rnw_i          <= '0';
						 
					 else
				  
						 npi_ns             <= RX_ADDR;
						 npi_req_set        <= '1';
						 npi_rnw_i          <= '1';

					 end if;
				  
				 when RX_WAIT_NOT_EMPTY   =>
					 
					 npi_rdfifo_pop_i   <= '0';
					 
					 -- Depending on Rd_FIFO_Latency, wait before popping read FIFO
					 if XIL_NPI_RdFIFO_Empty = '0' then
						 if XIL_NPI_RdFIFO_Latency = "10" then
							 npi_ns             		<= RX_WAIT_RXFIFO_LAT2;
							 npi_rdfifo_pop_i   		<= '0'; 
						 elsif XIL_NPI_RdFIFO_Latency = "01" then
							 npi_ns             <= RX_WAIT_RXFIFO_LAT1;
							 npi_rdfifo_pop_i   <= '0'; 
						 else
							 npi_ns           <= RX_POP;
							 npi_rdfifo_pop_i <= '1';		
						 end if;
					 else
						 npi_ns             <= RX_WAIT_NOT_EMPTY;
					 end if;
				  
				 when RX_WAIT_RXFIFO_LAT2 =>
					 -- First wait state for Latency = 2 
					 
					 npi_rdfifo_pop_i   <= '0';
					 npi_ns             <= RX_WAIT_RXFIFO_LAT1;
				 
				 when RX_WAIT_RXFIFO_LAT1 =>
				  -- Second wait state for Latency = 2
				  -- First wait state for Latency = 1
				  
					 npi_rdfifo_pop_i    <= '0';
					 npi_ns             	<= RX_POP;
					 Wr_FIFO_Write		  	<= '1'; 
				  
				 when RX_POP              =>
					 -- Continue to pop data until read FIFO empty
					 
					 if XIL_NPI_RdFIFO_Empty = '0' then
					 
						 npi_ns            		<= RX_POP;
						 
						 npi_rdfifo_pop_i 			<= '1';
						 Wr_FIFO_Write					<= '0';
						 Finish_transaction_NPI 	<= '0';
					 
					 else
					 -- Start over with another write/read
						 npi_ns             		<= IDLE_P;
						 
						 npi_rdfifo_pop_i   			<= '0';
						 Wr_FIFO_Write		  			<= '0';
						 Finish_transaction_NPI 	<= '1';
					 
					 end if;
				  
				 when IDLE_P  =>  
						  
					 -- Write the last word in the FIFO.
					 npi_ns            				<= IDLE;
					 
					 npi_rdfifo_pop_i   				<= '0';
					 Wr_FIFO_Write		  				<= '0';
					 Finish_transaction_NPI 		<= '0';
					  
				 end case;
				 
			 end process;


			 -- State machine synchronous logic
			 NPI_STATE_SYNC : process (XIL_NPI_Clk, XIL_NPI_Rst, initdone)
			 begin
				 if rising_edge(XIL_NPI_Clk) then
					 if ((XIL_NPI_Rst = '1') or (initdone = '0')) then
						 npi_cs <= RST;
					else
						npi_cs <= npi_ns;
					end if;
				end if;
			 end process;
			 
	 end arc_my_npi;

