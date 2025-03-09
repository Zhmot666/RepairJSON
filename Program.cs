using System;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Text.RegularExpressions;

class Program
{
    static void Main(string[] args)
    {
        string sourcePath = @"e:\Базы7\Экзон\Зарплата\ExtForms\";
        string targetPath = @"e:\22\3.json";

        try
        {
            // Получаем последний созданный json файл в директории
            var directory = new DirectoryInfo(sourcePath);
            var lastFile = directory.GetFiles("*.json")
                                  .OrderByDescending(f => f.LastWriteTime)
                                  .FirstOrDefault();

            if (lastFile == null)
            {
                Console.WriteLine("JSON файлы не найдены в указанной директории");
                return;
            }

            // Читаем содержимое файла
            string jsonContent = File.ReadAllText(lastFile.FullName);

            // Исправляем типичные ошибки в JSON
            jsonContent = FixJsonErrors(jsonContent);

            // Проверяем, является ли JSON валидным
            try
            {
                JsonDocument.Parse(jsonContent);
            }
            catch (JsonException ex)
            {
                Console.WriteLine($"Ошибка в структуре JSON: {ex.Message}");
                return;
            }

            // Создаем директорию назначения, если она не существует
            Directory.CreateDirectory(Path.GetDirectoryName(targetPath));

            // Записываем исправленный JSON в новый файл
            File.WriteAllText(targetPath, jsonContent);

            Console.WriteLine("Файл успешно обработан и сохранен");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Произошла ошибка: {ex.Message}");
        }
    }

    static string FixJsonErrors(string json)
    {
        // Удаляем BOM маркер, если он есть
        json = json.Trim('\uFEFF');
        
        // Заменяем неправильные кавычки на правильные
        json = json.Replace("'", "\"");
        
        // Удаляем лишние запятые перед закрывающими скобками
        json = Regex.Replace(json, ",\\s*([}\\]])", "$1");
        
        // Исправляем экранирование кавычек
        json = Regex.Replace(json, "(?<!\\\\)\\\\\"", "\"");
        
        return json;
    }
} 