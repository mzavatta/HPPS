----------------------------------------------------------------------------------------------------------------------------
-- Filename:        Top_bridge.vhd
-- Description:     
--                  
-- VHDL-Standard:   VHDL'93
-----------------------------------------------------------------------------------------------------------------------------
--------------------------------- LIBRARIES ---------------------------------------------------------------------------------
library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_unsigned.all;
use ieee.std_logic_arith.all;
-----------------------------------------------------------------------------------------------------------------------------


entity External_interface is

  generic(
		ADDR_WIDTH						: 	  integer															  := 32;
		DATA_WIDTH						: 	  integer															  := 32;
		INITIAL_ADDRESS_RANGE      :     std_logic_vector(31 downto 0)	                       := X"FFFF0000";
		FINAL_ADDRESS_RANGE		   :     std_logic_vector(31 downto 0)	                       := X"FFFFFFFF";
		BURST_LENGTH					:     std_logic_vector(3 downto 0)				  				  := "0101" );
	 
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
	npi_wrfifo_be  					: out std_logic_vector(7 downto 0);
	
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
	S_out_STORE							: out std_logic

	);
  
end entity;


architecture Behavioural of External_interface is

	type FSM_STATE is (IDLE, RESET_ST, LOAD, LOAD_EXT, LOAD_INT, STORE, STORE_EXT, STORE_INT,WAIT_state,WAIT_state_load);
	signal state, nxt_state: FSM_STATE;
	signal READ_DATA_int,READ_DATA_1, READ_DATA_2, READ_DATA_3 : std_logic_vector(63 downto 0);
	
	signal S_in_addr_REG							: std_logic_vector(ADDR_WIDTH-1 downto 0);
	signal S_in_size_REG							: std_logic_vector(7 downto 0);
	signal S_in_data_w_REG						: std_logic_vector(DATA_WIDTH-1 downto 0);
	
	signal debug_status							: std_logic_vector(2 downto 0);
	signal S_in_LOAD_prev,S_in_STORE_prev : std_logic;
	signal npi_wrfifo_be_32, npi_wrfifo_be_16, npi_wrfifo_be_8 : std_logic_vector(7 downto 0);
	signal WRITE_DATA_32, WRITE_DATA_16,WRITE_DATA_8	: std_logic_vector(DATA_WIDTH-1 downto 0);

	
begin

------------------------------ Debug Signals --------------------------------------

	process (state)
	begin
		case state is
			when IDLE => debug_status 					<= "000";
			when WAIT_state => debug_status 			<= "001";
			when LOAD => debug_status					<= "010";
			when LOAD_INT => debug_status 			<= "011";
			when LOAD_EXT => debug_status 			<= "100";
			when STORE => debug_status 				<= "101";
			when STORE_INT => debug_status 			<= "110"; 
			when STORE_EXT => debug_status 			<= "111";
			when WAIT_state_load => debug_status 	<= "001";
			when others => debug_status 				<= "111";
		end case;
	end process;

	DEBUG_EI <= IN_READY_load & S_in_LOAD & S_in_STORE & debug_status;
	debug_S_in_size_REG <= S_in_size_REG; --S_in_size_REG; 
	debug_S_in_addr_REG <= S_in_addr_REG; 
	debug_READ_DATA_1 <= READ_DATA_3; 
	
--------------------------------------------------------------------------------------

--------------------------------- INPUT REGISTERS ------------------------------------

	Input_REG: process(CLK,RESET, state)
	begin
		if (RESET = '1') then
			S_in_addr_REG	<= (others => '0');
			S_in_data_w_REG<= (others => '0');
		elsif (CLK'event and CLK = '1') then
			if (state =  IDLE) and ((S_in_LOAD = '1') or (S_in_STORE = '1')) then 
				S_in_addr_REG		<= S_in_addr;
				S_in_data_w_REG	<= S_in_data_w;
			end if;
		end if;
	end process;


	Input_REG2: process(CLK,RESET)
	begin
		if (RESET = '1') then
			S_in_size_REG	<= (others => '0');
		elsif (CLK'event and CLK = '1') then
		
			S_in_LOAD_prev 	<= S_in_LOAD;
			S_in_STORE_prev 	<= S_in_STORE;
			
			if ((((S_in_LOAD_prev = '1')and(S_in_LOAD = '0')) or ((S_in_LOAD_prev = '0')and(S_in_LOAD = '1')))or
				(((S_in_STORE_prev = '1')and(S_in_STORE = '0')) or ((S_in_STORE_prev = '0')and(S_in_STORE = '1')))) then
				S_in_size_REG		<= S_in_size;
			end if;
			
		end if;
	end process;
	
-------------------------------------------------------------------------------------------
	
	
	State_reg: process(CLK, RESET)
	begin
		if(RESET = '1') then
			state 	<= IDLE;
		else
			if (CLK'event) and (CLK = '1') then
				state 	<= nxt_state;
			end if;
		end if;
	end process;
	


	next_state_FSM: process(RESET,state,S_in_LOAD,S_in_STORE,S_in_addr_REG,IN_READY, IN_READY_load)
		begin
		
			if(RESET = '1') then
				nxt_state <= IDLE;
			else
				case(state) is 
				
				when RESET_ST => 
				nxt_state <= IDLE;
				
				when IDLE =>
					if (S_in_LOAD = '1')and(IN_READY = '0') then 
						nxt_state <= LOAD;
					elsif(S_in_STORE = '1')and(IN_READY = '0') then  
						nxt_state <= STORE;
					else 
						nxt_state <= IDLE;
					end if;
				
				when WAIT_state => 
					
					if (IN_READY = '0')  then 
						nxt_state <= WAIT_state;
					else
						nxt_state <=  RESET_ST;
					end if;
					
					
				when WAIT_state_load => 
					
					if (IN_READY_load = '0')  then 
						nxt_state <= WAIT_state_load;
					else
						nxt_state <=  RESET_ST;
					end if;

				when LOAD =>
					
					if ( S_in_addr_REG < FINAL_ADDRESS_RANGE) and (S_in_addr_REG > INITIAL_ADDRESS_RANGE)  then 
						nxt_state <= LOAD_INT;
					else
						nxt_state <=  LOAD_EXT;
					end if;
				
				when LOAD_INT =>
					
					nxt_state <=  WAIT_state_load;

				when LOAD_EXT =>
					
					nxt_state <=  IDLE;
					
				when STORE =>
					
					if ( S_in_addr_REG < FINAL_ADDRESS_RANGE) and (S_in_addr_REG > INITIAL_ADDRESS_RANGE)  then 
						nxt_state <= STORE_INT;
					else
						nxt_state <=  STORE_EXT;
					end if;

				when STORE_INT =>
				
					nxt_state <= WAIT_state;

				when STORE_EXT => 
					
					nxt_state <=  IDLE;
					
				end case;
			end if;
		end process;
						

	output_assign: process(clk)
	begin
	
	if (RESET = '1') then
				
		S_out_addr							<= (others => '0');
		S_out_size							<= (others => '0');
		S_out_data_w						<= (others => '0');
		S_out_data_r						<= (others => '0');
		S_out_ready							<= '0';
		S_out_LOAD							<= '0';
		S_out_STORE							<= '0';
		
		--WRITE_DATA							<=  (others => '0');
		OUTPUT_ADDRESS						<=  (others => '0');
		INSTRUCTION							<=  "00";
	
	else
		if (clk'event) and (clk = '1') then
			case(state) is
			
			when IDLE | LOAD | STORE | RESET_ST => 
				
				S_out_addr							<= (others => '0');
				S_out_size							<= (others => '0');
				S_out_data_w						<= (others => '0');
				S_out_ready							<= '0';
				S_out_data_r						<= (others => '0');				
				S_out_LOAD							<= '0';
				S_out_STORE							<= '0';
				
				--WRITE_DATA							<=  (others => '0');
				OUTPUT_ADDRESS						<=  (others => '0');
				INSTRUCTION							<=  "00";
			
			when WAIT_state => 
				
				S_out_addr							<= (others => '0');
				S_out_size							<= (others => '0');
				S_out_data_w						<= (others => '0');
				
				S_out_LOAD							<= '0';
				S_out_STORE							<= '0';
				
				--WRITE_DATA							<=  (others => '0');
				OUTPUT_ADDRESS						<=  (others => '0');
				INSTRUCTION							<=  "00";
				
				S_out_ready							<= IN_READY;
				S_out_data_r						<= READ_DATA_int;
				
			when WAIT_state_load => 
				
				S_out_addr							<= (others => '0');
				S_out_size							<= (others => '0');
				S_out_data_w						<= (others => '0');
				
				S_out_LOAD							<= '0';
				S_out_STORE							<= '0';
				
				--WRITE_DATA							<=  (others => '0');
				OUTPUT_ADDRESS						<=  (others => '0');
				INSTRUCTION							<=  "00";
				
				S_out_ready							<= IN_READY_load;
				S_out_data_r						<= READ_DATA_int;

		
			when(LOAD_INT) =>
			
				S_out_addr							<= S_in_addr_REG;
				S_out_size							<= (others => '0');
				S_out_data_w						<= (others => '0');
				S_out_data_r						<= (others => '0');
				S_out_ready							<= '0'; 
				S_out_LOAD							<= '0';
				S_out_STORE							<= '0';
				
				--WRITE_DATA							<=  (others => '0');
				OUTPUT_ADDRESS						<=  S_in_addr_REG;
				INSTRUCTION							<=  "01";
			
			when (LOAD_EXT) =>
			
				S_out_addr							<= S_in_addr_REG;
				S_out_size							<= S_in_size_REG;
				S_out_data_w						<= S_in_data_w_REG;
				S_out_data_r						<= (others => 'X');
				S_out_ready							<= '0';
				S_out_LOAD							<= '1';
				S_out_STORE							<= '0';

				--WRITE_DATA							<=  (others => '0');
				OUTPUT_ADDRESS						<=  (others => '0');
				INSTRUCTION							<=  "00";
				
			when (STORE_INT) =>
			
				S_out_addr							<= S_in_addr_REG;
				S_out_size							<= (others => '0');
				S_out_data_w						<= (others => '0');
				S_out_data_r						<= (others => '0');
				S_out_ready							<= '0'; 
				S_out_LOAD							<= '0';
				S_out_STORE							<= '0';

				--WRITE_DATA							<=  S_in_data_w_REG;
				OUTPUT_ADDRESS						<=  S_in_addr_REG(31 downto 3)&"000";
				INSTRUCTION							<=  "10";
			
			when (STORE_EXT) =>
			
				S_out_addr							<= S_in_addr_REG;
				S_out_size							<= S_in_size_REG;
				S_out_data_w						<= S_in_data_w_REG;
				S_out_data_r						<= (others => 'X');
				S_out_ready							<= '0';
				S_out_LOAD							<= '0';
				S_out_STORE							<= '1';	
				
				--WRITE_DATA							<=  (others => '0');
				OUTPUT_ADDRESS						<=  (others => '0');
				INSTRUCTION							<=  "00";
			
			end case;
		end if;
	end if;
	end process;
	
	
	-----------------------------------------------------------------------------------------------------
	-- MUXs to adapt the size of the Write Signal to the size of the Data Transference
	
	WriteMUX: process (S_in_size_REG, npi_wrfifo_be_32, npi_wrfifo_be_16, npi_wrfifo_be_8, WRITE_DATA_32, WRITE_DATA_16,WRITE_DATA_8)
	begin
		case S_in_size_REG is 
			when "00000110" => -- 64
				npi_wrfifo_be   <= "11111111";
				WRITE_DATA		 <= S_in_data_w_REG;				
			when "00100000" =>   -- 32
				npi_wrfifo_be   <= npi_wrfifo_be_32;
				WRITE_DATA		 <= WRITE_DATA_32;
			when "00000010" => -- 16
				npi_wrfifo_be    <= npi_wrfifo_be_16;
				WRITE_DATA		 <= WRITE_DATA_16;
			when "00000000" =>  -- 8
				npi_wrfifo_be   <= npi_wrfifo_be_8;
				WRITE_DATA		 <= WRITE_DATA_8;
			when others => 
				npi_wrfifo_be   <= "00000000";
				WRITE_DATA		 <= S_in_data_w_REG;
	end case;
	end process;
			
		-- 32 Bits MUX
	WriteMUX_8: process (S_in_addr_REG,S_in_data_w_REG)
	begin 
		case S_in_addr_REG(2 downto 0) is 
			when "000" => -- 64
				npi_wrfifo_be_8 <= "00000001";
				WRITE_DATA_8	 <= S_in_data_w_REG;
			when "001" => -- 64
				npi_wrfifo_be_8 <= "00000010";
				WRITE_DATA_8	 <= X"000000" & S_in_data_w_REG(7 downto 0) & X"0";
			when "010" => -- 64
				npi_wrfifo_be_8 <= "00000100";
				WRITE_DATA_8	 <= X"00000" & S_in_data_w_REG(7 downto 0) & X"00";
			when "011" => -- 64
				npi_wrfifo_be_8 <= "00001000";
				WRITE_DATA_8	 <= X"0000" & S_in_data_w_REG(7 downto 0) & X"000";
			when "100" => -- 64
				npi_wrfifo_be_8 <= "00010000";
				WRITE_DATA_8	 <= X"000" & S_in_data_w_REG(7 downto 0) & X"0000";
			when "101" => -- 64
				npi_wrfifo_be_8 <= "00100000";
				WRITE_DATA_8	 <= X"00" & S_in_data_w_REG(7 downto 0) & X"00000";
			when "110" => -- 64
				npi_wrfifo_be_8 <= "01000000";
				WRITE_DATA_8	 <= X"0" & S_in_data_w_REG(7 downto 0) & X"000000";
			when "111" => -- 64
				npi_wrfifo_be_8 <= "10000000";
				WRITE_DATA_8	 <= S_in_data_w_REG(7 downto 0) & X"000000";				
			when others => 
				npi_wrfifo_be_8 <= "00000000";
				WRITE_DATA_8	 <= S_in_data_w_REG;
		end case;
	end process;
	
		-- 16 Bits MUX
	WriteMUX_16: process (S_in_addr_REG, S_in_data_w_REG)
	begin 
		case S_in_addr_REG(2 downto 1) is 
			when "00" => -- 64
				npi_wrfifo_be_16 <= "00000011";
				WRITE_DATA_16	  <= S_in_data_w_REG;
			when "01" => -- 64
				npi_wrfifo_be_16 <= "00001100";
				WRITE_DATA_16	  <= X"0000" & S_in_data_w_REG(15 downto 0) & X"00";
			when "10" => -- 64
				npi_wrfifo_be_16 <= "00110000";
				WRITE_DATA_16	  <= X"00" & S_in_data_w_REG(15 downto 0) & X"0000";
			when "11" => -- 64
				npi_wrfifo_be_16 <= "11000000";
				WRITE_DATA_16	  <= S_in_data_w_REG(15 downto 0) & X"000000";				
			when others => 
				npi_wrfifo_be_32 <= "00000000";
				WRITE_DATA_16	  <= S_in_data_w_REG;
		end case;
	end process;	
	
	-- 32 Bits MUX
	WriteMUX_32: process (S_in_addr_REG, S_in_data_w_REG)
	begin 
		case S_in_addr_REG(2) is 
			when '0' => -- 64
				npi_wrfifo_be_32 <= "00001111";
				WRITE_DATA_32 <= S_in_data_w_REG;
			when '1' => -- 64
				npi_wrfifo_be_32 <= "11110000";	
				WRITE_DATA_32 <= S_in_data_w_REG(31 downto 0) & X"00000000";				
			when others => 
				npi_wrfifo_be_32 <= "00000000";
				WRITE_DATA_32 <= S_in_data_w_REG;
		end case;
	end process;	

	----------------------------------------------------------------------------------------------------------
	-- MUXs to adapt the size of the Read Signal to the size of the Data Transference

	ReadMUX: process (S_in_size_REG,READ_DATA_3)
	begin
	case S_in_size_REG is 
      when "00000110" => READ_DATA_int <= READ_DATA_3(63 downto 0);    -- 64
      when "00100000" => READ_DATA_int <= X"00000000" & READ_DATA_3(31 downto 0); -- 32
      when "00000010" => READ_DATA_int <= X"000000000000" & READ_DATA_3(15 downto 0);  -- 16 
      when "00000000" => READ_DATA_int <= X"00000000000000" & READ_DATA_3(7 downto 0);  -- 8
      when others => READ_DATA_int <= (others =>'1');
   end case;
	end process;
	
	ReadMUX_1: process (READ_DATA, S_in_addr_REG)
	begin
		if(S_in_addr_REG(2) = '1') then 
			READ_DATA_1 <= X"00000000" & READ_DATA(63 downto 32);
		else
			READ_DATA_1 <= READ_DATA(63 downto 0);
		end if;
	end process;
	
	ReadMUX_2: process (READ_DATA_1, S_in_addr_REG)
	begin
		if(S_in_addr_REG(1) = '1') then 
			READ_DATA_2 <= X"0000" & READ_DATA_1(63 downto 16);
		else
			READ_DATA_2 <= READ_DATA_1(63 downto 0);
		end if;
	end process;
	
	
	ReadMUX_3: process (READ_DATA_2, S_in_addr_REG)
	begin
		if(S_in_addr_REG(0) = '1') then 
			READ_DATA_3 <= X"00" & READ_DATA_2(63 downto 8);
		else
			READ_DATA_3 <= READ_DATA_2(63 downto 0);
		end if;
	end process;

end;
