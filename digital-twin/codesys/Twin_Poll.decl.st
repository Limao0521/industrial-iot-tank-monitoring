PROGRAM Twin_Poll
VAR
    client : ModbusFB.ClientTCP;
    reader : ModbusFB.ClientRequestReadInputRegisters;
    address : ARRAY [0..3] OF BYTE := [127, 0, 0, 1];
    words : ARRAY [0..7] OF UINT;
    connect : BOOL := TRUE;
    retry : TON;
    interval : TON;
    stale : TON;
    phase : USINT;
    validFrame : BOOL;
END_VAR
