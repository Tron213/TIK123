from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

TOKEN = '
TARGET_USER_ID = 288832250

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class Form(StatesGroup):
    first_message = State()  # Первое текстовое сообщение
    second_message = State()  # Второе текстовое сообщение
    third_message = State()  # Третье текстовое сообщение
    file = State()  # Файл

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await Form.first_message.set()
    await message.reply("Здравствуйте, приветствуем вас в кадровом боте компании НПП ТИК! Пожалуйста, напишите на какую должность вы претендуете .")

@dp.message_handler(state=Form.first_message)
async def process_first_message(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['first_message'] = message.text
    await Form.next()
    await message.reply("Отлично! Напишите ваше имя.")

@dp.message_handler(state=Form.second_message)
async def process_second_message(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['second_message'] = message.text
    await Form.next()
    await message.reply("Замечательно! Сколько вам полных лет?.")

@dp.message_handler(state=Form.third_message)
async def process_third_message(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['third_message'] = message.text
    await Form.next()
    await message.reply("Почти готово! Теперь отправьте файл с вашим резюме в формате docx или pdf.")

@dp.message_handler(content_types=['document'], state=Form.file)
async def process_file(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['file_id'] = message.document.file_id
        data['file_caption'] = message.caption
    
    # Отправка собранных данных пользователю с TARGET_USER_ID
    
    info = [data['first_message'], data['second_message'], data['third_message']]
    info = [msg for msg in info if msg is not None]  # Фильтруем пустые сообщения
    caption = "\n".join(info) + "\n\n" + (data['file_caption'] if data['file_caption'] is not None else '')
    
    custom_text = f"Новая заявка для отдела кадров от ползователя @{message.from_user.username}"
    final_caption =  custom_text + "\n\n" + caption
    
    inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
    inline_keyboard.add(types.InlineKeyboardButton("Принято ✅", callback_data="accepted"), types.InlineKeyboardButton("Отклонено ❌", callback_data="rejected"))
    await bot.send_document(TARGET_USER_ID, data['file_id'], caption=final_caption, reply_markup=inline_keyboard)
    
   
    await message.answer("Все данные отправлены!Благодарим вас за уделенное время, постараемся связаться в свами в кротчайшие сроки")

    await state.finish()
   
@dp.callback_query_handler(lambda callback_query: True)
async def process_callback(callback_query: types.CallbackQuery):
    message = callback_query.message
    inline_keyboard = types.InlineKeyboardMarkup()
    if callback_query.data == "accepted":
        await bot.answer_callback_query(callback_query.id, "Заявка принята, свяжитесь с соискателем и назначьте собеседование", show_alert=True)
        # Удаляем кнопку "Отклонено"
        inline_keyboard.add(types.InlineKeyboardButton("Принято ✅", callback_data="accepted"))
    elif callback_query.data == "rejected":
        await bot.answer_callback_query(callback_query.id, "Заявка отклонена", show_alert=True)
        # Удаляем кнопку "Принято"
        inline_keyboard.add(types.InlineKeyboardButton("Отклонено ❌", callback_data="rejected"))
    else:
        await bot.answer_callback_query(callback_query.id, "Неизвестный callback_data", show_alert=True)
        return
    
    await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message.message_id, reply_markup=inline_keyboard)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
