import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  const origin=request.headers.get("origin");
  if(origin && origin!==request.nextUrl.origin) return NextResponse.json({error:"Origen no permitido."},{status:403});
  let body;
  try { body=await request.json(); } catch { return NextResponse.json({error:"Solicitud inválida."},{status:400}); }
  if(!body || typeof body!=="object" || typeof body.message!=="string" || !body.message.trim() || body.message.length>20000 || typeof body.conversationId!=="string" || !/^[a-zA-Z0-9-]{1,64}$/.test(body.conversationId)) return NextResponse.json({error:"Mensaje o conversación inválidos."},{status:400});
  const password=process.env.OCD_DEMO_PASSWORD;
  if(!password)return NextResponse.json({error:"Falta configurar OCD_DEMO_PASSWORD en el servidor."},{status:503});
  const cookieName="ocd_"+body.conversationId;
  const session=request.cookies.get(cookieName)?.value;
  try {
    const upstream=await fetch(new URL("/api/chat",process.env.OCD_API_URL||"https://app-production-b27a3c5e.up.railway.app"),{
      method:"POST",redirect:"error",cache:"no-store",signal:AbortSignal.timeout(120000),
      headers:{"Content-Type":"application/json",Authorization:"Basic "+Buffer.from((process.env.OCD_DEMO_USERNAME||"demo")+":"+password).toString("base64"),...(session?{Cookie:"ocd_session="+session}:{})},
      body:JSON.stringify({message:body.message.trim()})
    });
    if(!upstream.ok)return NextResponse.json({error:upstream.status===401?"El backend rechazó las credenciales.":"El backend no pudo procesar el mensaje.",upstreamStatus:upstream.status},{status:502});
    const data=await upstream.json();
    if(!data || typeof data!=="object" || typeof data.answer!=="string")return NextResponse.json({error:"Respuesta del backend no compatible."},{status:502});
    const response=NextResponse.json(data,{headers:{"Cache-Control":"no-store"}});
    const sessionCookie=upstream.headers.getSetCookie().find(value=>value.startsWith("ocd_session="));
    if(sessionCookie){
      const value=sessionCookie.split(";")[0].slice("ocd_session=".length);
      response.cookies.set(cookieName,value,{httpOnly:true,sameSite:"strict",secure:request.nextUrl.protocol==="https:",path:"/api/chat"});
    }
    return response;
  } catch { return NextResponse.json({error:"No se pudo contactar al agente. Intenta enviar el mensaje nuevamente."},{status:502}); }
}
