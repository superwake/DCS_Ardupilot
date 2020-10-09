local default_output_file = nil

function LuaExportStart()
	-- default_output_file = io.open(lfs.writedir().."/Logs/Export.log", "w")
	package.path  = package.path..";"..lfs.currentdir().."/LuaSocket/?.lua"
	package.cpath = package.cpath..";"..lfs.currentdir().."/LuaSocket/?.dll"
	socket = require("socket")
	host = "localhost"

	port = 8001
	c = socket.try(socket.connect(host, port)) -- connect to the listener socket
	c:setoption("tcp-nodelay",true) -- set immediate transmission mode

end

function LuaExportBeforeNextFrame()

end

function LuaExportAfterNextFrame()
	local t = LoGetModelTime()
	local name = LoGetPilotName()
	local o = LoGetSelfData()
	local WorldVel = LoGetVectorVelocity()
	local IndicatedAirSpeed = LoGetIndicatedAirSpeed()
	local TrueAirSpeed = LoGetTrueAirSpeed()
	local BarometricPressure = LoGetBasicAtmospherePressure()
	local AltitudeAboveSeaLevel = LoGetAltitudeAboveSeaLevel()
	local AltitudeAboveGroundLevel = LoGetAltitudeAboveGroundLevel()
	local AngularVelocity = LoGetAngularVelocity()
	local AccelerationUnits = LoGetAccelerationUnits()
	local VectorVelocity = LoGetVectorVelocity()
	local MechInfo = LoGetMechInfo()
	local EngineInfo = LoGetEngineInfo()

	local Elev = (MechInfo.controlsurfaces.elevator.left + MechInfo.controlsurfaces.elevator.right) / 2
	local Ailr = (MechInfo.controlsurfaces.eleron.left*-1 + MechInfo.controlsurfaces.eleron.right) + 1 -- ailerons deflect in opposite direction
	local Rudd = (MechInfo.controlsurfaces.rudder.left + MechInfo.controlsurfaces.rudder.right) / 2 * -1 

	socket.try(c:send(string.format("Time=%.3f, name=%s, V_ind=%.3f, V_tru=%.3f, Norml=%.3f, Axial=%.3f, Side=%.3f, Q=%.3f, P=%.3f, R=%.3f, Pitch=%.3f, Roll=%.3f, Hding=%.3f, Lat=%.7f, Lon=%.7f, BaroPress=%.5f, Alt=%.3f, RAlt=%.3f, Pos_E=%.3f, Pos_U=%.3f, Pos_S=%.3f, Vel_E=%.3f, Vel_U=%.3f, Vel_S=%.3f, Elev=%.3f, Ailr=%.3f, Rudd=%.3f\n", t, name, IndicatedAirSpeed, TrueAirSpeed, AccelerationUnits.y, AccelerationUnits.x*-1, AccelerationUnits.z*-1, AngularVelocity.z, AngularVelocity.x, AngularVelocity.y*-1, o.Pitch*57.2958, o.Bank*57.2958, o.Heading*57.2958, o.LatLongAlt.Lat, o.LatLongAlt.Long, BarometricPressure, AltitudeAboveSeaLevel, AltitudeAboveGroundLevel, o.Position.z, o.Position.y, -o.Position.x, WorldVel.z, WorldVel.y, -WorldVel.x, Elev, Ailr, Rudd)))

end

function LuaExportStop()
   -- if default_output_file then
	  -- default_output_file:close()
	  -- default_output_file = nil
   -- end
	socket.try(c:send("quit")) -- to close the listener socket
	c:close()
	-- u:close()
end

function LuaExportActivityNextEvent(t)
	local tNext = t

	return tNext
end