client(xConnect := connect, aIPaddr := address, uiPort := 1502);
retry(IN := NOT connect, PT := T#1s);
IF client.xError THEN
    connect := FALSE;
END_IF;
IF retry.Q THEN
    connect := TRUE;
END_IF;

interval(IN := phase = 0 AND client.xConnected, PT := T#200ms);
IF interval.Q THEN
    phase := 1;
END_IF;
reader(rClient := client, xExecute := phase = 1,
    uiUnitId := 1, uiStartItem := 0, uiQuantity := 8, pData := ADR(words),
    udiReplyTimeout := 300000, udiTimeOut := 750000);

validFrame := FALSE;
IF phase = 1 THEN
    IF reader.xDone THEN
        phase := 2;
        validFrame := words[6] = 16#A231 AND words[0] <= 7 AND words[1] <= 7
            AND words[2] <= 1 AND words[3] <= 5 AND words[4] <= 1 AND words[5] <= 1
            AND words[7] <= 1;
        GVL.ModbusOK := validFrame;
    ELSIF reader.xError OR NOT client.xConnected THEN
        phase := 2;
        GVL.ModbusOK := FALSE;
    END_IF;
ELSIF phase = 2 THEN
    phase := 0;
END_IF;

stale(IN := NOT validFrame, PT := T#1s);
IF stale.Q OR NOT client.xConnected THEN
    GVL.ModbusOK := FALSE;
END_IF;

GVL.B1 := GVL.ModbusOK AND ((words[1] AND 1) <> 0);
GVL.B2 := GVL.ModbusOK AND ((words[1] AND 2) <> 0);
GVL.B3 := GVL.ModbusOK AND ((words[1] AND 4) <> 0);
GVL.SystemActive := GVL.ModbusOK AND words[2] = 1;
GVL.H1 := GVL.SystemActive AND words[3] = 1;
GVL.H2 := GVL.SystemActive AND words[3] = 2;
GVL.H3 := GVL.SystemActive AND words[3] = 3;
GVL.H4 := GVL.SystemActive AND words[3] = 4;
GVL.H5 := GVL.SystemActive AND words[3] = 5;
GVL.RemoteOverride := GVL.ModbusOK AND words[4] = 1;
GVL.SerialInputs := GVL.ModbusOK AND words[7] = 1;
